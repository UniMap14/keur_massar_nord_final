from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.serializers import serialize
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count
from django.contrib.gis.db.models.functions import AsGeoJSON, GeomOutputGeoFunc
from django.db import connection


class Simplify(GeomOutputGeoFunc):
    """
    Django n'expose pas ST_Simplify nativement (contrairement à AsGeoJSON) :
    on l'enveloppe soi-même. Génère du SQL : ST_Simplify(geom, tolerance).
    Utilisé pour alléger les géométries envoyées au navigateur sur la carte
    (indispensable à l'échelle de ~40 000 parcelles).
    """
    function = "ST_Simplify"
    arity = 2


class SimplifyPreserveTopology(GeomOutputGeoFunc):
    """
    Comme Simplify, mais via ST_SimplifyPreserveTopology : garantit une
    géométrie toujours valide (jamais NULL/vide), contrairement à
    ST_Simplify qui peut faire disparaître une toute petite parcelle avec
    une tolérance trop grossière -- ce qui faisait planter json.loads()
    sur la vue d'ensemble complète (40 000 parcelles).
    """
    function = "ST_SimplifyPreserveTopology"
    arity = 2
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import json
from decimal import Decimal, ROUND_HALF_UP

from .permissions import a_role
from .models import Signalement
from .forms import SignalementForm

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .forms import SimulateurFiscalForm


from .forms import ContactForm
from .forms import ContribuableForm, PaiementForm
from .forms import DemandeImmatriculationForm
from .forms import DemandeMutationForm
from .models import (
    Parcelle,
    Propriétaire,
    Contribuable,
    Paiement,
    Zone,
    Taxation,
    TypeTaxe,
    GuideFiscal,
    CategorieInfrastructure,
    Infrastructure,
    Actualite,
    ProfilCitoyen,
)
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Prefetch


def _est_agent(user):
    # Tout compte staff ne suffit plus : il faut aussi detenir un role
    # reconnu (technique ou fiscal). Superviseur et comptes historiques
    # sans groupe assigne restent couverts par a_role() (retrocompatibilite).
    return user.is_staff and a_role(user, 'technique', 'fiscal')


def home_page(request):
    """Affiche la page d'accueil du système foncier et fiscal."""

    total_parcelles = Parcelle.objects.count()
    total_proprietaires = Propriétaire.objects.count()

    total_taxes = (
        Parcelle.objects.aggregate(total=Sum("montant_taxe_annuelle"))["total"]
        or 0
    )

    parcelles_en_retard = Parcelle.objects.filter(
        statut_fiscal="EN_RETARD"
    ).count()

    top_retardaires = (
        Parcelle.objects.filter(statut_fiscal="EN_RETARD")
        .order_by("-montant_taxe_annuelle")[:5]
    )

    quartiers = (
        Parcelle.objects.exclude(adresse_parcelle="")
        .values("adresse_parcelle")
        .annotate(nb_parcelles=Count("id"))
        .order_by("adresse_parcelle")[:8]
    )

    actualites = Actualite.objects.filter(publie=True)[:3]

    # Bandeau d'actualités défilant (ticker) : les titres les plus récents,
    # toutes catégories confondues, indépendamment des 3 déjà affichées
    # en cartes plus bas.
    actualites_ticker = (
        Actualite.objects.filter(publie=True)
        .order_by("-date_publication", "-date_creation")
        .values("pk", "titre", "date_publication")[:8]
    )

    # --- Indicateurs de transparence (page d'accueil) : chiffres reels,
    # jamais inventes. Si aucun signalement n'existe encore, le taux de
    # resolution est affiche a 0 plutot que de provoquer une erreur.
    from .models import Infrastructure, Signalement
    nb_infrastructures_total = Infrastructure.objects.count()
    nb_signalements_total = Signalement.objects.count()
    nb_signalements_resolus = Signalement.objects.filter(statut='RESOLU').count()
    pct_signalements_resolus = (
        round((nb_signalements_resolus / nb_signalements_total) * 100)
        if nb_signalements_total > 0 else 0
    )

    context = {
        "total_parcelles": total_parcelles,
        "total_proprietaires": total_proprietaires,
        "total_taxes": total_taxes,
        "parcelles_en_retard": parcelles_en_retard,
        "top_retardaires": top_retardaires,
        "quartiers": quartiers,
        "nb_infrastructures_total": nb_infrastructures_total,
        "nb_signalements_resolus": nb_signalements_resolus,
        "pct_signalements_resolus": pct_signalements_resolus,

        # --- panneau "en chiffres" du hero ---
        # Chiffres démographiques/administratifs saisis manuellement pour
        # le moment (données non issues de la base). À remplacer par des
        # requêtes réelles quand les données correspondantes seront prêtes.
        'population': "224 765",
        'superficie': "13,18",
        'nb_quartiers': 86,
        'annee_creation': 2021,

        # --- infrastructures / signalements pour la section 3 colonnes ---
        # Comptage RÉEL par catégorie (Infrastructure.categorie), au lieu
        # de chiffres fictifs codés en dur. Si aucune infrastructure n'est
        # encore recensée en base, la liste est vide et le template
        # affiche un message honnête plutôt que des données inventées.
        'infrastructures': (
            CategorieInfrastructure.objects
            .annotate(total=Count('infrastructures'))
            .filter(total__gt=0)
            .order_by('ordre', 'label')
            .values('icone', 'label', 'total')
        ),
        # Les signalements citoyens sont confidentiels : ils sont traités
        # par l'administration dans l'espace de gestion, jamais affichés
        # publiquement (ni titre, ni lieu, ni photo).
        'actualites': actualites,
        'actualites_ticker': actualites_ticker,
    }
    return render(request, 'foncier/home.html', context)


# ============================================================
# GÉOPORTAIL — VUE PUBLIQUE
# ============================================================

def carte_geoportail(request):
    """Affiche la page publique du geoportail (aucune donnee fiscale).
    Si le visiteur est un citoyen connecte dont le compte est relie a
    une parcelle (NICAD existant), celle-ci est transmise au template
    pour que "Me geolocaliser" puisse indiquer sa zone et la distance
    jusqu'a sa propre parcelle."""
    import json
    from .models import Parcelle

    mes_parcelles_geojson = None
    citoyen = getattr(request.user, "citoyen", None) if request.user.is_authenticated else None
    if citoyen is not None and citoyen.numero_foncier:
        parcelles = Parcelle.objects.filter(nicad=citoyen.numero_foncier)
        features = []
        for p in parcelles:
            try:
                geometrie = json.loads(p.geom.geojson)
            except Exception:
                continue
            features.append({
                "type": "Feature",
                "geometry": geometrie,
                "properties": {"nicad": p.nicad, "adresse": p.adresse_parcelle},
            })
        if features:
            mes_parcelles_geojson = json.dumps({"type": "FeatureCollection", "features": features})

    return render(request, "foncier/geoportail.html", {
        "mes_parcelles_geojson": mes_parcelles_geojson,
    })


# ============================================================
# GÉOPORTAIL — VUE ADMIN (réservée aux agents)
# ============================================================

@login_required
@user_passes_test(_est_agent)
def carte_geoportail_admin(request):
    """
    Affiche la carte du géoportail réservée aux agents (is_staff) : statut
    fiscal, montants, propriétaire et édition depuis un panneau latéral.
    """
    return render(request, "foncier/geoportail_admin.html", {"active_section": "geoportail"})


# ============================================================
# TABLEAU DE BORD FISCAL — PAGE PUBLIQUE (aucune donnée individuelle)
# ============================================================

def fiscalite(request):
    """
    Page publique : cadre général, infos particuliers/entreprises, procédures,
    simulateur, guides fiscaux, et calendrier des échéances des taxes
    communales.

    Aucune donnée fiscale n'est affichée ici, pas même agrégée : le nombre
    de contribuables et les montants (taxes émises, encaissées, restant à
    recouvrer) sont volontairement retirés de cette page publique. Ils
    restent consultables par les agents dans le tableau de bord de gestion
    (protégé par connexion).
    """

    # Guides fiscaux (DGID) regroupés par catégorie dans le template
    guides_fiscaux = GuideFiscal.objects.all().order_by("categorie", "titre")

    # Taxes communales avec leur prochaine échéance calculée, triées de la
    # plus proche à la plus lointaine (celles sans échéance configurée en
    # dernier). Icône + description de secours par code, au cas où l'agent
    # n'a pas encore rempli la description en base.
    INFOS_PAR_CODE = {
        "FONCIERE": ("fa-house", "ic-re", "Due par tout propriétaire d'une parcelle bâtie ou non bâtie sur le territoire de la commune."),
        "PATENTE": ("fa-store", "ic-pu", "Contribution des commerçants et artisans exerçant une activité sur le territoire communal."),
        "OCCUPATION": ("fa-user-large", "ic-or", "Applicable à l'occupation temporaire ou permanente du domaine public communal."),
        "MARCHE": ("fa-basket-shopping", "ic-gr", "Perçue auprès des commerçants installés sur les marchés municipaux."),
        "ASSAINISSEMENT": ("fa-droplet", "ic-bl", "Contribution au financement de l'entretien du réseau d'assainissement communal."),
        "PUBLICITE": ("fa-bullhorn", "ic-te", "Due pour l'installation de supports publicitaires sur le territoire de la commune."),
    }

    types_taxe = list(TypeTaxe.objects.all())
    for t in types_taxe:
        t.echeance_calculee = t.prochaine_echeance()
        t.jours_restants_calcules = t.jours_restants()
        icone, classe_icone, description_defaut = INFOS_PAR_CODE.get(
            t.code, ("fa-file-invoice-dollar", "ic-re", "")
        )
        t.icone_fa = icone
        t.classe_icone = classe_icone
        t.description_affichee = t.description or description_defaut
    types_taxe.sort(
        key=lambda t: (t.echeance_calculee is None, t.echeance_calculee or t.libelle)
    )

    context = {
        "guides_fiscaux": guides_fiscaux,
        "types_taxe": types_taxe,
    }

    return render(request, "foncier/fiscalite.html", context)


def guide_fiscal_detail(request, code):
    guide = get_object_or_404(GuideFiscal, code=code)
    return render(request, "foncier/guide_fiscal_detail.html", {"guide": guide})


# ============================================================
# API GEOJSON PARCELLES — VERSION PUBLIQUE
# Aucune donnée fiscale (statut, montant, valeur locative, propriétaire).
# Voir api_parcelles_geojson_admin pour la version réservée aux agents.
# ============================================================

TOLERANCE_SIMPLIFICATION = 0.00002
TOLERANCE_SIMPLIFICATION_TOUTES = 0.00003  # formes reconnaissables meme pour les petites parcelles

CACHE_KEY_PUBLIC = "geojson_parcelles_public"
CACHE_KEY_ADMIN = "geojson_parcelles_admin"
CACHE_TTL_SECONDES = 120  # invalidé de toute façon dès qu'une parcelle est modifiée
CACHE_KEY_ZONES = "geojson_zones"
CACHE_KEY_SECTIONS = "geojson_sections"
CACHE_KEY_LIMITES = "geojson_limites"

# La commune compte ~38 000 parcelles : les envoyer TOUTES au navigateur en un
# seul GeoJSON (comme le faisait ce fichier avant) fait planter/bloquer la
# carte (requête PostGIS trop lourde + Leaflet incapable d'afficher 38 000
# polygones d'un coup). On limite donc désormais chaque réponse à la zone
# visible de la carte (bbox) ET à un plafond de sécurité, même si la zone
# demandée contient encore trop de parcelles.
PARCELLES_MAX_PAR_REQUETE = 10000


def _bbox_depuis_requete(request):
    """
    Lit le paramètre ?bbox=west,south,east,north envoyé par Leaflet
    (bounds.toBBoxString()) et renvoie un Polygon PostGIS, ou None si absent
    /invalide.
    """
    from django.contrib.gis.geos import Polygon

    bbox = request.GET.get("bbox")
    if not bbox:
        return None
    try:
        west, south, east, north = [float(v) for v in bbox.split(",")]
        return Polygon.from_bbox((west, south, east, north))
    except (ValueError, TypeError):
        return None


def api_parcelles_geojson(request):
    """
    Renvoie les Parcelle en GeoJSON pour l'affichage public du géoportail,
    limitées à la zone actuellement visible sur la carte (paramètre bbox)
    et plafonnées à PARCELLES_MAX_PAR_REQUETE, pour rester utilisable avec
    ~38 000 parcelles en base. Sans bbox, on ne renvoie rien plutôt que de
    tenter de tout charger d'un coup.
    """
    bbox_poly = _bbox_depuis_requete(request)
    if bbox_poly is None:
        return JsonResponse({"type": "FeatureCollection", "features": []})

    features = []

    qs = (
        Parcelle.objects
        .exclude(geom__isnull=True)
        .filter(geom__bboverlaps=bbox_poly)
        .select_related("zone")
        .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION)))
        .only(
            "id", "nicad", "superficie", "adresse_parcelle",
            "occupation_sol", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier",
            "zone__nom",
        )
        .order_by("id")[:PARCELLES_MAX_PAR_REQUETE]
    )

    for parcelle in qs.iterator():
        features.append({
            "type": "Feature",
            "geometry": json.loads(parcelle.geojson_geom),
            "properties": {
                "nicad": parcelle.nicad,
                "num_lot": parcelle.nicad,
                "numero_parcelle": parcelle.numero_parcelle,
                "numero_lot": parcelle.numero_lot,
                "section_cadastrale": parcelle.section_cadastrale,
                "numero_titre_foncier": parcelle.numero_titre_foncier,
                "superficie": parcelle.superficie,
                "adresse_parcelle": parcelle.adresse_parcelle,
                "occupation_sol": parcelle.occupation_sol,
                "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
            },
        })

    return JsonResponse({"type": "FeatureCollection", "features": features})


def api_parcelles_toutes_geojson(request):
    """
    Renvoie TOUTES les parcelles (aucun plafond), avec une géométrie
    fortement simplifiée, pour l'affichage en vue d'ensemble de toute la
    commune (dézoomé). Le résultat est mis en cache indéfiniment et
    recalculé uniquement quand une parcelle change (voir le signal
    _invalider_cache_parcelles plus bas) : sans ce cache, recalculer la
    simplification de ~40 000 géométries à chaque requête serait trop lent.
    """
    data = cache.get(CACHE_KEY_PUBLIC)
    if data is None:
        qs = (
            Parcelle.objects
            .exclude(geom__isnull=True)
            .filter(parcelle_active=True)
            .select_related("zone")
            .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))
            .only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "occupation_sol", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier",
                "zone__nom",
            )
            .order_by("id")
        )

        infra_par_parcelle = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            details_publics = {k: v for k, v in (infra.details or {}).items() if k != "Nombre d'employés"}
            infra_par_parcelle.setdefault(infra.parcelle_id, []).append({
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": details_publics,
            })

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": {
                    "nicad": parcelle.nicad,
                    "num_lot": parcelle.nicad,
                    "numero_parcelle": parcelle.numero_parcelle,
                    "numero_lot": parcelle.numero_lot,
                    "section_cadastrale": parcelle.section_cadastrale,
                    "numero_titre_foncier": parcelle.numero_titre_foncier,
                    "superficie": parcelle.superficie,
                    "adresse_parcelle": parcelle.adresse_parcelle,
                    "occupation_sol": parcelle.occupation_sol,
                    "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                    "infrastructures": infra_par_parcelle.get(parcelle.id, []),
                },
            }
            for parcelle in qs.iterator()
        ]
        infra_sans_parcelle = [
            {
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": {k: v for k, v in (infra.details or {}).items() if k != "Nombre d'employés"},
            }
            for infra in Infrastructure.objects.filter(parcelle_id__isnull=True).select_related("categorie")
        ]

        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle}
        cache.set(CACHE_KEY_PUBLIC, data, None)  # pas d'expiration : invalidé par le signal

    return JsonResponse(data)


# ============================================================
# API GEOJSON PARCELLES — VERSION ADMIN
# Inclut statut fiscal, montants, valeur locative, propriétaire.
# Réservée aux agents (is_staff). Ne jamais exposer publiquement.
# ============================================================

@login_required
@user_passes_test(_est_agent)
def api_parcelles_geojson_admin(request):
    """
    GeoJSON ADMIN des parcelles : inclut le statut fiscal, les montants de
    taxe, la valeur locative, le type de document et le propriétaire.
    Réservé aux agents (is_staff). Limité à la zone visible (bbox) et
    plafonné à PARCELLES_MAX_PAR_REQUETE — voir api_parcelles_geojson.
    """
    bbox_poly = _bbox_depuis_requete(request)
    if bbox_poly is None:
        return JsonResponse({"type": "FeatureCollection", "features": []})

    features = []

    qs = (
        Parcelle.objects
        .exclude(geom__isnull=True)
        .filter(geom__bboverlaps=bbox_poly)
        .select_related("zone", "proprietaire")
        .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION)))
        .only(
            "id", "nicad", "superficie", "adresse_parcelle",
            "montant_taxe_annuelle", "valeur_locative", "statut_fiscal",
            "type_document", "reference_arrete", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier", "occupation_sol", "simulation_fiscale",
            "zone__nom", "proprietaire__nom", "proprietaire__prenom",
        )
        .order_by("id")[:PARCELLES_MAX_PAR_REQUETE]
    )

    for parcelle in qs.iterator():
        features.append({
            "type": "Feature",
            "geometry": json.loads(parcelle.geojson_geom),
            "properties": {
                "id": parcelle.id,
                "nicad": parcelle.nicad,
                "num_lot": parcelle.nicad,
                "superficie": parcelle.superficie,
                "adresse_parcelle": parcelle.adresse_parcelle,
                "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                "valeur_locative": float(parcelle.valeur_locative),
                "statut_fiscal": parcelle.statut_fiscal,
                "type_document": parcelle.type_document,
                "reference_arrete": parcelle.reference_arrete,
                "section_cadastrale": parcelle.section_cadastrale,
                "numero_parcelle": parcelle.numero_parcelle,
                "numero_lot": parcelle.numero_lot,
                "numero_titre_foncier": parcelle.numero_titre_foncier,
                "occupation_sol": parcelle.occupation_sol,
                "simulation_fiscale": parcelle.simulation_fiscale,
                "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                "proprietaire": (
                    f"{parcelle.proprietaire.prenom} {parcelle.proprietaire.nom}"
                    if parcelle.proprietaire_id else None
                ),
            },
        })

    return JsonResponse({"type": "FeatureCollection", "features": features})


@login_required
@user_passes_test(_est_agent)
def api_parcelles_toutes_geojson_admin(request):
    """Équivalent admin de api_parcelles_toutes_geojson : toutes les
    parcelles, géométrie fortement simplifiée, avec les infos fiscales en
    plus (pour la coloration par statut sur la vue d'ensemble). Mis en
    cache séparément (CACHE_KEY_ADMIN)."""
    data = cache.get(CACHE_KEY_ADMIN)
    if data is None:
        qs = (
            Parcelle.objects
            .exclude(geom__isnull=True)
            .filter(parcelle_active=True)
            .select_related("zone", "proprietaire")
            .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))
            .only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "montant_taxe_annuelle", "valeur_locative", "statut_fiscal",
                "type_document", "reference_arrete", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier", "occupation_sol", "simulation_fiscale",
                "zone__nom", "proprietaire__nom", "proprietaire__prenom",
            )
            .order_by("id")
        )

        infra_par_parcelle_admin = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle_admin.setdefault(infra.parcelle_id, []).append({
                "id": infra.id,
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": infra.details,
            })

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": {
                    "id": parcelle.id,
                    "nicad": parcelle.nicad,
                    "num_lot": parcelle.nicad,
                    "superficie": parcelle.superficie,
                    "adresse_parcelle": parcelle.adresse_parcelle,
                    "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                    "valeur_locative": float(parcelle.valeur_locative),
                    "statut_fiscal": parcelle.statut_fiscal,
                    "type_document": parcelle.type_document,
                    "reference_arrete": parcelle.reference_arrete,
                "section_cadastrale": parcelle.section_cadastrale,
                "numero_parcelle": parcelle.numero_parcelle,
                "numero_lot": parcelle.numero_lot,
                "numero_titre_foncier": parcelle.numero_titre_foncier,
                    "occupation_sol": parcelle.occupation_sol,
                    "infrastructures": infra_par_parcelle_admin.get(parcelle.id, []),
                    "simulation_fiscale": parcelle.simulation_fiscale,
                    "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                    "proprietaire": (
                        f"{parcelle.proprietaire.prenom} {parcelle.proprietaire.nom}"
                        if parcelle.proprietaire_id else None
                    ),
                },
            }
            for parcelle in qs.iterator()
        ]
        infra_sans_parcelle_admin = [
            {
                "id": infra.id,
                "nom": infra.nom,
                "categorie": infra.categorie.label,
                "icone": infra.categorie.icone,
                "couleur": infra.categorie.couleur,
                "latitude": infra.latitude,
                "longitude": infra.longitude,
                "sous_type": infra.sous_type,
                "details": infra.details,
            }
            for infra in Infrastructure.objects.filter(parcelle_id__isnull=True).select_related("categorie")
        ]

        data = {"type": "FeatureCollection", "features": features, "infrastructures_hors_parcelle": infra_sans_parcelle_admin}
        cache.set(CACHE_KEY_ADMIN, data, None)

    return JsonResponse(data)


@login_required
@user_passes_test(_est_agent)
@require_POST
def parcelle_update_fiscal(request, parcelle_id):
    """
    Met à jour les informations d'une parcelle depuis la carte admin :
    identifiant NICAD, statut fiscal, montant de taxe, valeur locative,
    adresse, type de document, occupation du sol, référence d'arrêté, et
    propriétaire (recherché par numéro CNI). Réservé aux agents (is_staff).
    """
    try:
        parcelle = Parcelle.objects.get(pk=parcelle_id)
    except Parcelle.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Parcelle introuvable."}, status=404)

    # --- Controle de role selon les champs soumis (edition depuis la carte) ---
    # Un Gestionnaire/Chef Cadastre peut modifier les champs cadastraux, mais
    # pas les champs fiscaux, et inversement pour le service Fiscalite. Le
    # Superviseur (et un compte historique sans role assigne) passe toujours
    # via a_role(). Evite qu'un agent d'un service modifie les donnees de
    # l'autre service via ce point d'entree (contrairement au dashboard
    # classique qui etait deja correctement restreint).
    CHAMPS_CADASTRAUX = {
        "nicad", "adresse_parcelle", "type_document", "occupation_sol",
        "reference_arrete", "section_cadastrale", "numero_parcelle",
        "numero_lot", "numero_titre_foncier", "proprietaire_cni",
    }
    CHAMPS_FISCAUX = {"statut_fiscal", "montant_taxe_annuelle", "valeur_locative"}

    champs_soumis = set(request.POST.keys())
    if (champs_soumis & CHAMPS_CADASTRAUX) and not a_role(request.user, 'technique'):
        return JsonResponse({
            "ok": False,
            "error": "Vous n'avez pas les droits pour modifier les informations cadastrales de cette parcelle."
        }, status=403)
    if (champs_soumis & CHAMPS_FISCAUX) and not a_role(request.user, 'fiscal'):
        return JsonResponse({
            "ok": False,
            "error": "Vous n'avez pas les droits pour modifier les informations fiscales de cette parcelle."
        }, status=403)

    champs_modifies = []

    # --- Identifiant NICAD ---
    # Modifiable depuis le panneau d'édition du géoportail admin. On
    # vérifie qu'aucune autre parcelle n'utilise déjà ce NICAD avant
    # d'enregistrer, pour éviter les doublons d'identifiant.
    nicad = request.POST.get("nicad")
    if nicad is not None:
        nicad = nicad.strip()
        if not nicad:
            return JsonResponse({"ok": False, "error": "Le NICAD ne peut pas être vide."}, status=400)
        deja_utilise = (
            Parcelle.objects.filter(nicad=nicad).exclude(pk=parcelle.pk).exists()
        )
        if deja_utilise:
            return JsonResponse({
                "ok": False,
                "error": f"Le NICAD « {nicad} » est déjà utilisé par une autre parcelle."
            }, status=400)
        parcelle.nicad = nicad
        champs_modifies.append("nicad")

    statut = request.POST.get("statut_fiscal")
    if statut:
        statuts_valides = {choix[0] for choix in Parcelle.STATUTS_FISCAUX}
        if statut not in statuts_valides:
            return JsonResponse({"ok": False, "error": "Statut fiscal invalide."}, status=400)
        parcelle.statut_fiscal = statut
        champs_modifies.append("statut_fiscal")

    montant = request.POST.get("montant_taxe_annuelle")
    if montant not in (None, ""):
        try:
            parcelle.montant_taxe_annuelle = float(montant)
            champs_modifies.append("montant_taxe_annuelle")
            # Un agent qui saisit un montant à la main fournit une vraie
            # donnée : ça n'est plus une simulation, le badge doit disparaître.
            if parcelle.simulation_fiscale:
                parcelle.simulation_fiscale = False
                champs_modifies.append("simulation_fiscale")
        except ValueError:
            return JsonResponse({"ok": False, "error": "Montant de taxe invalide."}, status=400)

    valeur_locative = request.POST.get("valeur_locative")
    if valeur_locative not in (None, ""):
        try:
            parcelle.valeur_locative = float(valeur_locative)
            champs_modifies.append("valeur_locative")
        except ValueError:
            return JsonResponse({"ok": False, "error": "Valeur locative invalide."}, status=400)

    adresse = request.POST.get("adresse_parcelle")
    if adresse is not None:
        parcelle.adresse_parcelle = adresse.strip()
        champs_modifies.append("adresse_parcelle")

    type_document = request.POST.get("type_document")
    if type_document:
        types_valides = {choix[0] for choix in Parcelle.TYPES_DOCUMENT}
        if type_document not in types_valides:
            return JsonResponse({"ok": False, "error": "Type de document invalide."}, status=400)
        parcelle.type_document = type_document
        champs_modifies.append("type_document")

    occupation_sol = request.POST.get("occupation_sol")
    if occupation_sol is not None:
        parcelle.occupation_sol = occupation_sol.strip()
        champs_modifies.append("occupation_sol")

    reference_arrete = request.POST.get("reference_arrete")
    if reference_arrete is not None:
        parcelle.reference_arrete = reference_arrete.strip()
        champs_modifies.append("reference_arrete")

    section_cadastrale = request.POST.get("section_cadastrale")
    if section_cadastrale is not None:
        parcelle.section_cadastrale = section_cadastrale.strip()
        champs_modifies.append("section_cadastrale")

    numero_parcelle = request.POST.get("numero_parcelle")
    if numero_parcelle is not None:
        parcelle.numero_parcelle = numero_parcelle.strip()
        champs_modifies.append("numero_parcelle")

    numero_lot = request.POST.get("numero_lot")
    if numero_lot is not None:
        parcelle.numero_lot = numero_lot.strip()
        champs_modifies.append("numero_lot")

    numero_titre_foncier = request.POST.get("numero_titre_foncier")
    if numero_titre_foncier is not None:
        parcelle.numero_titre_foncier = numero_titre_foncier.strip()
        champs_modifies.append("numero_titre_foncier")

    # Propriétaire : recherché par numéro CNI. Champ vide = pas de changement.
    # "RETIRER" = détache le propriétaire actuel.
    cni = request.POST.get("proprietaire_cni")
    if cni and cni.strip():
        if cni.strip().upper() == "RETIRER":
            parcelle.proprietaire = None
            champs_modifies.append("proprietaire")
        else:
            try:
                proprietaire = Propriétaire.objects.get(ni_cni=cni.strip())
                parcelle.proprietaire = proprietaire
                champs_modifies.append("proprietaire")
            except Propriétaire.DoesNotExist:
                return JsonResponse({
                    "ok": False,
                    "error": f"Aucun propriétaire avec la CNI {cni.strip()}. "
                             f"Crée-le d'abord dans l'admin Django (Propriétaires)."
                }, status=400)

    if champs_modifies:
        parcelle.save(update_fields=champs_modifies)

    return JsonResponse({
        "ok": True,
        "id": parcelle.id,
        "nicad": parcelle.nicad,
        "superficie": parcelle.superficie,
        "statut_fiscal": parcelle.statut_fiscal,
        "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
        "valeur_locative": float(parcelle.valeur_locative),
        "adresse_parcelle": parcelle.adresse_parcelle,
        "type_document": parcelle.type_document,
        "occupation_sol": parcelle.occupation_sol,
        "simulation_fiscale": parcelle.simulation_fiscale,
        "reference_arrete": parcelle.reference_arrete,
                "section_cadastrale": parcelle.section_cadastrale,
                "numero_parcelle": parcelle.numero_parcelle,
                "numero_lot": parcelle.numero_lot,
                "numero_titre_foncier": parcelle.numero_titre_foncier,
        "proprietaire": (
            f"{parcelle.proprietaire.prenom} {parcelle.proprietaire.nom}"
            if parcelle.proprietaire_id else None
        ),
    })


# ============================================================
# API GEOJSON ZONES
# ============================================================

def api_zones_geojson(request):
    """
    Calque "Zones/Quartiers" : quartiers officiels importes dans le
    modele QuartierOfficiel (remplace l'ancienne requete SQL brute sur
    la table temporaire kmsn_quartier).
    Mis en cache indéfiniment (invalidé par le signal
    _invalider_cache_zones) : ces quartiers changent tres rarement, pas
    la peine de refaire le tour de la table a chaque chargement de la
    carte, sur les deux geoportails.
    """
    data = cache.get(CACHE_KEY_ZONES)
    if data is None:
        from foncier.models import QuartierOfficiel

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(q.geom.geojson),
                "properties": {"nom": q.nom},
            }
            for q in QuartierOfficiel.objects.all()
        ]
        data = json.dumps({"type": "FeatureCollection", "features": features})
        cache.set(CACHE_KEY_ZONES, data, None)

    return HttpResponse(data, content_type="application/json")


def api_sections_geojson(request):
    """Calque "Sections cadastrales" : sections officielles importees.
    Mis en cache indéfiniment (invalidé par le signal
    _invalider_cache_sections)."""
    data = cache.get(CACHE_KEY_SECTIONS)
    if data is None:
        from foncier.models import SectionCadastrale

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(s.geom.geojson),
                "properties": {"numero": s.numero},
            }
            for s in SectionCadastrale.objects.all()
        ]
        data = json.dumps({"type": "FeatureCollection", "features": features})
        cache.set(CACHE_KEY_SECTIONS, data, None)

    return HttpResponse(data, content_type="application/json")


def api_limites_geojson(request):
    """Calque "Limites administratives" : limite(s) officielle(s) de la
    commune. Mis en cache indéfiniment (invalidé par le signal
    _invalider_cache_limites)."""
    data = cache.get(CACHE_KEY_LIMITES)
    if data is None:
        from foncier.models import LimiteAdministrative

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(l.geom.geojson),
                "properties": {"nom": l.nom},
            }
            for l in LimiteAdministrative.objects.all()
        ]
        data = json.dumps({"type": "FeatureCollection", "features": features})
        cache.set(CACHE_KEY_LIMITES, data, None)

    return HttpResponse(data, content_type="application/json")


# ============================================================
# ESPACE PERSONNEL DU CONTRIBUABLE — SEULE PAGE QUI MONTRE
# DES DONNÉES INDIVIDUELLES, ET UNIQUEMENT CELLES DE l'UTILISATEUR CONNECTÉ
# ============================================================

@login_required
def contribuable_create(request):
    if request.method == 'POST':
        form = ContribuableForm(request.POST)
        if form.is_valid():
            contribuable = form.save()
            messages.success(request, f"Contribuable « {contribuable} » créé avec succès.")
            return redirect('contribuable_create')
    else:
        form = ContribuableForm()

    return render(request, 'foncier/contribuable_form.html', {'form': form})


@login_required
def paiement_create(request):
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save()
            messages.success(
                request,
                f"Paiement de {paiement.montant:.0f} FCFA enregistré "
                f"(reçu {paiement.numero_recu})."
            )
            return redirect('paiement_create')
    else:
        form = PaiementForm()

    return render(request, 'foncier/paiement_form.html', {'form': form})


# ============================================================
# CONTACT
# ============================================================

def mentions_legales(request):
    """Page légale statique : identité de l'éditeur, hébergement,
    propriété intellectuelle. Ne contient aucune donnée personnelle."""
    return render(request, 'foncier/mentions_legales.html')


def politique_confidentialite(request):
    """Politique de confidentialité : quelles données sont collectées
    sur ce site, pourquoi, combien de temps, et comment les citoyens
    peuvent exercer leurs droits (accès, rectification, suppression)."""
    return render(request, 'foncier/politique_confidentialite.html')


def contact(request):
    """Affiche le formulaire de contact et traite son envoi."""

    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            message_contact = form.save()

            # Envoi d'un email de notification à l'administration
            try:
                send_mail(
                    subject=f"[Contact KMSN] {message_contact.sujet}",
                    message=(
                        f"Nouveau message reçu via le formulaire de contact.\n\n"
                        f"Nom : {message_contact.nom}\n"
                        f"Email : {message_contact.email}\n"
                        f"Téléphone : {message_contact.telephone or 'Non renseigné'}\n\n"
                        f"Message :\n{message_contact.message}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(
                request,
                "Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais."
            )
            return redirect('contact')

        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = ContactForm()

    return render(request, "foncier/contact.html", {"form": form})


BAREME_IR = [
    (Decimal("0"),        Decimal("630000"),    Decimal("0.00")),
    (Decimal("630000"),   Decimal("1500000"),   Decimal("0.20")),
    (Decimal("1500000"),  Decimal("4000000"),   Decimal("0.30")),
    (Decimal("4000000"),  Decimal("8000000"),   Decimal("0.35")),
    (Decimal("8000000"),  Decimal("13500000"),  Decimal("0.37")),
    (Decimal("13500000"), Decimal("50000000"),  Decimal("0.40")),
    (Decimal("50000000"), None,                 Decimal("0.43")),
]


def _arrondi(valeur):
    return int(valeur.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _calcul_ir_bareme(quotient):
    """Applique le barème progressif à un quotient (RNI / nombre de parts)."""
    impot = Decimal("0")
    detail = []
    for bas, haut, taux in BAREME_IR:
        if quotient <= bas:
            break
        plafond = haut if haut is not None else quotient
        fraction = min(quotient, plafond) - bas
        if fraction > 0:
            montant = fraction * taux
            impot += montant
            detail.append({
                "tranche": f"{int(bas):,} – {int(plafond):,} FCFA".replace(",", " "),
                "taux": float(taux) * 100,
                "montant": _arrondi(montant),
            })
    return impot, detail


def _calculer_parts(situation, nb_enfants):
    """Quotient familial CGI : 1 part (célibataire) ou 1,5 (marié) + 0,5/enfant,
    plafonné à 5 parts."""
    parts = Decimal("1.5") if situation == "marie" else Decimal("1")
    parts += Decimal("0.5") * min(int(nb_enfants or 0), 12)
    return min(parts, Decimal("5"))


@require_POST
def simuler_fiscalite(request):
    form = SimulateurFiscalForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    data = form.cleaned_data
    type_sim = data["type_simulation"]
    revenu = data["revenu"]

    resultat = {"ok": True, "type": type_sim}

    if type_sim == "ir":
        parts = _calculer_parts(data["situation_familiale"], data["nombre_enfants"])
        quotient = revenu / parts
        impot_quotient, detail = _calcul_ir_bareme(quotient)
        impot_brut = impot_quotient * parts

        resultat.update({
            "revenu_net_imposable": _arrondi(revenu),
            "parts": float(parts),
            "quotient_par_part": _arrondi(quotient),
            "impot": _arrondi(impot_brut),
            "detail_tranches": detail,
            "taux_effectif": round(float(impot_brut / revenu * 100), 2) if revenu else 0,
            "net_apres_impot": _arrondi(revenu - impot_brut),
            "reference": "Barème progressif Art. 173 CGI (7 tranches, 0 % à 43 %) "
                         "+ quotient familial (1 à 5 parts). Simulation indicative — "
                         "hors TRIMF et déductions spécifiques (pensions, assurance-vie, "
                         "intérêts d'emprunt immobilier).",
        })

    elif type_sim == "is":
        benefice = revenu
        ca_ht = data.get("chiffre_affaires_is") or benefice

        is_calcule = benefice * Decimal("0.30") if benefice > 0 else Decimal("0")

        imf = ca_ht * Decimal("0.005")
        imf = max(Decimal("500000"), min(imf, Decimal("5000000")))

        deficitaire = benefice <= 0
        imf_applicable = deficitaire or is_calcule < imf
        impot_final = imf if imf_applicable else is_calcule

        resultat.update({
            "benefice_imposable": _arrondi(benefice),
            "chiffre_affaires_ht": _arrondi(ca_ht),
            "is_calcule": _arrondi(is_calcule),
            "imf_calcule": _arrondi(imf),
            "regime_applique": "IMF" if imf_applicable else "IS",
            "impot": _arrondi(impot_final),
            "reference": "IS = 30 % du bénéfice imposable. Impôt Minimum Forfaitaire "
                         "(IMF) = 0,5 % du CA HT si déficit ou si IS < IMF "
                         "(plancher 500 000 FCFA, plafond 5 000 000 FCFA).",
        })

    elif type_sim == "tva":
        tva = revenu * Decimal("0.18")
        resultat.update({
            "chiffre_affaires_ht": _arrondi(revenu),
            "impot": _arrondi(tva),
            "reference": "TVA au taux normal de 18 % (Livre II du CGI, "
                         "Directive UEMOA n°02/98/CM). Taux réduit de 10 % pour "
                         "l'hôtellerie/tourisme non couvert par cette simulation.",
        })

    elif type_sim == "cgu":
        secteur = data["secteur_activite"]
        est_bien = secteur == "bien"
        taux = Decimal("0.02") if est_bien else Decimal("0.05")
        plancher = Decimal("25000") if est_bien else Decimal("30000")
        seuil = Decimal("50000000") if est_bien else Decimal("25000000")

        cgu = max(revenu * taux, plancher)
        depasse_seuil = revenu > seuil

        resultat.update({
            "chiffre_affaires_ttc": _arrondi(revenu),
            "taux_applique": float(taux) * 100,
            "impot": _arrondi(cgu),
            "depasse_seuil_cgu": depasse_seuil,
            "seuil_cgu": _arrondi(seuil),
            "reference": f"CGU = {float(taux) * 100:.0f} % du CA TTC "
                         f"({'biens' if est_bien else 'services'}), plancher "
                         f"{int(plancher):,} FCFA. Régime réservé aux CA ≤ "
                         f"{int(seuil):,} FCFA.".replace(",", " "),
        })

    else:
        return JsonResponse({"ok": False, "errors": "Type d'impôt inconnu."}, status=400)

    return JsonResponse(resultat)


def galerie(request):
    """Page publique presentant la galerie photo de la commune."""
    from .models import PhotoGalerie
    photos = PhotoGalerie.objects.order_by('ordre', '-date_ajout')
    return render(request, 'foncier/galerie.html', {'photos': photos})


def cartotheque(request):
    """Page publique presentant les cartes thematiques d'analyse (MNT, pente, etc.)."""
    from .models import CarteThematique
    cartes = list(CarteThematique.objects.order_by('ordre', '-date_ajout'))

    # Badge thematique calcule a la volee (pas de champ en base, donc aucune
    # migration necessaire) : simple reconnaissance de mots-cles dans le titre.
    regles_theme = [
        ('occupation du sol', 'Occupation du sol'),
        ('pente', 'Relief & pentes'),
        ('drainage', 'Hydrologie'),
        ('densité', 'Infrastructures'),
        ('scolaire', 'Éducation'),
        ('santé', 'Santé'),
    ]
    for c in cartes:
        titre_minuscule = c.titre.lower()
        c.theme = 'Analyse territoriale'
        for mot_cle, libelle in regles_theme:
            if mot_cle in titre_minuscule:
                c.theme = libelle
                break

    return render(request, 'foncier/cartotheque.html', {'cartes': cartes})


def foncier_info(request):
    """Ancienne page dediee au foncier, desormais fusionnee dans l'onglet
    'Foncier' de la page Fiscalite. Redirige vers ce nouvel emplacement."""
    return redirect('/fiscalite/#panel-foncier')


def recherche_globale(request):
    """Recherche simple sur le site : actualites et cartotheque."""
    from django.db.models import Q
    from .models import Actualite, CarteThematique

    requete = request.GET.get('q', '').strip()
    actualites_trouvees = []
    cartes_trouvees = []

    if requete:
        actualites_trouvees = Actualite.objects.filter(
            Q(titre__icontains=requete) | Q(chapo__icontains=requete)
        ).order_by('-date_publication')[:20]

        cartes_trouvees = CarteThematique.objects.filter(
            Q(titre__icontains=requete) | Q(explication__icontains=requete)
        ).order_by('ordre')[:20]

    total = len(actualites_trouvees) + len(cartes_trouvees)

    return render(request, 'foncier/recherche_globale.html', {
        'q': requete,
        'actualites_trouvees': actualites_trouvees,
        'cartes_trouvees': cartes_trouvees,
        'total': total,
    })


def signalement(request):
    if request.method == 'POST':
        form = SignalementForm(request.POST, request.FILES)
        if form.is_valid():
            objet = form.save()

            # Notification interne à l'administration (best-effort : un
            # email qui échoue ne doit jamais empêcher le citoyen de
            # recevoir sa confirmation).
            try:
                lien_dashboard = request.build_absolute_uri(
                    reverse('dashboard_signalement_detail', args=[objet.pk])
                )
                send_mail(
                    subject=f"[KEUR MASSAR NORD] Nouveau signalement : {objet.titre}",
                    message=(
                        f"Un nouveau signalement citoyen a été déposé.\n\n"
                        f"Titre : {objet.titre}\n"
                        f"Lieu : {objet.lieu}\n"
                        f"Date : {objet.date_signalement:%d/%m/%Y %H:%M}\n\n"
                        f"Voir et traiter ce signalement :\n{lien_dashboard}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.NOTIF_AGENTS_EMAIL,
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, "Votre signalement a bien été enregistré. Merci pour votre contribution.")
            return redirect('signalement_confirmation', reference=objet.reference)
    else:
        form = SignalementForm()

    # Les signalements sont confidentiels : ils ne sont plus listés ici.
    # Ils sont visibles uniquement par l'administration, dans l'espace
    # de gestion (/gestion/signalements/).
    return render(request, 'foncier/signalement.html', {
        'form': form,
    })


def signalement_confirmation(request, reference):
    """Affichée juste après l'envoi d'un signalement : donne au citoyen son
    code de suivi personnel, à conserver pour vérifier l'évolution de son
    signalement plus tard, sans avoir besoin de créer de compte."""
    objet = get_object_or_404(Signalement, reference=reference)
    return render(request, 'foncier/signalement_confirmation.html', {
        'signalement': objet,
    })


def signalement_suivi(request):
    """Suivi public et anonyme d'un signalement à partir de son code de
    suivi secret (UUID) : ne montre JAMAIS la note interne de l'agent, ni
    aucune information sur les autres signalements."""
    code = request.GET.get('reference', '').strip()
    objet = None
    recherche_effectuee = bool(code)
    erreur = None

    if code:
        try:
            objet = Signalement.objects.get(reference=code)
        except (Signalement.DoesNotExist, ValueError, ValidationError):
            erreur = "Aucun signalement ne correspond à ce code. Vérifiez qu'il est bien complet."

    return render(request, 'foncier/signalement_suivi.html', {
        'code': code,
        'signalement': objet,
        'recherche_effectuee': recherche_effectuee,
        'erreur': erreur,
    })


def statistiques(request):
    import json
    from django.db.models import Avg, Case, When, Value, CharField as _CF

    context = {
        'population': "224 765",        # RGPH-5 (2023), ANSD
        'annee_population': 2023,
        'superficie': "13,18",
        'densite': "17 058",
        'pop_hommes_pct': "50,7",
        'pop_femmes_pct': "49,3",
        'nb_quartiers': 86,
        'annee_creation': 2021,
        # Valeurs numériques "propres" (sans virgule ni espace), utilisées
        # par l'animation des chiffres sur la page.
        'population_val': 224765,
        'superficie_val': 13.18,
        'densite_val': 17058,
        'pop_hommes_pct_val': 50.7,
        'pop_femmes_pct_val': 49.3,
        'nb_quartiers_val': 86,
        'annee_creation_val': 2021,
    }

    # --- Données cadastrales réelles (calculées à partir des parcelles
    # effectivement importées en base, pas de chiffres inventés) ---
    nb_parcelles = Parcelle.objects.count()
    context['nb_parcelles'] = nb_parcelles

    if nb_parcelles:
        superficie_totale_m2 = (
            Parcelle.objects.aggregate(total=Sum('superficie'))['total'] or 0
        )
        context['superficie_cadastree_ha'] = round(superficie_totale_m2 / 10000, 1)

        superficie_moyenne_m2 = (
            Parcelle.objects.aggregate(moy=Avg('superficie'))['moy'] or 0
        )
        context['superficie_moyenne_m2'] = round(superficie_moyenne_m2, 1)

        # Nombre de parcelles par quartier (top 15, pour rester lisible
        # sur un graphique).
        parcelles_par_quartier = list(
            Parcelle.objects
            .exclude(zone__isnull=True)
            .values('zone__nom')
            .annotate(total=Count('id'))
            .order_by('-total')[:15]
        )
        context['parcelles_par_quartier'] = parcelles_par_quartier
        context['chart_quartiers_labels'] = json.dumps(
            [q['zone__nom'] for q in parcelles_par_quartier]
        )
        context['chart_quartiers_valeurs'] = json.dumps(
            [q['total'] for q in parcelles_par_quartier]
        )

        # Répartition des parcelles par taille (tranches de superficie).
        tranches_ordre = [
            '< 100 m²', '100 - 300 m²', '300 - 600 m²',
            '600 - 1 000 m²', '1 000 - 5 000 m²', '> 5 000 m²',
        ]
        repartition_taille_brute = (
            Parcelle.objects
            .exclude(superficie__isnull=True)
            .annotate(
                tranche=Case(
                    When(superficie__lt=100, then=Value(tranches_ordre[0])),
                    When(superficie__lt=300, then=Value(tranches_ordre[1])),
                    When(superficie__lt=600, then=Value(tranches_ordre[2])),
                    When(superficie__lt=1000, then=Value(tranches_ordre[3])),
                    When(superficie__lt=5000, then=Value(tranches_ordre[4])),
                    default=Value(tranches_ordre[5]),
                    output_field=_CF(),
                )
            )
            .values('tranche')
            .annotate(total=Count('id'))
        )
        totaux_par_tranche = {r['tranche']: r['total'] for r in repartition_taille_brute}
        context['chart_taille_labels'] = json.dumps(tranches_ordre)
        context['chart_taille_valeurs'] = json.dumps(
            [totaux_par_tranche.get(t, 0) for t in tranches_ordre]
        )

    # --- Infrastructures publiques réellement recensées ---
    context['nb_infrastructures'] = Infrastructure.objects.count()
    repartition_infrastructures = list(
        CategorieInfrastructure.objects
        .annotate(total=Count('infrastructures'))
        .filter(total__gt=0)
        .order_by('-total')
    )
    context['repartition_infrastructures'] = repartition_infrastructures
    context['chart_infra_labels'] = json.dumps(
        [c.label for c in repartition_infrastructures]
    )
    context['chart_infra_valeurs'] = json.dumps(
        [c.total for c in repartition_infrastructures]
    )
    context['chart_infra_couleurs'] = json.dumps(
        [getattr(c, 'couleur', None) or '#2f7a4f' for c in repartition_infrastructures]
    )

    # Infrastructures par quartier (top 15).
    infra_par_quartier = list(
        Infrastructure.objects
        .exclude(quartier='')
        .exclude(quartier__isnull=True)
        .values('quartier')
        .annotate(total=Count('id'))
        .order_by('-total')[:15]
    )
    context['infra_par_quartier'] = infra_par_quartier
    context['chart_infra_quartier_labels'] = json.dumps(
        [q['quartier'] for q in infra_par_quartier]
    )
    context['chart_infra_quartier_valeurs'] = json.dumps(
        [q['total'] for q in infra_par_quartier]
    )

    return render(request, 'foncier/statistiques.html', context)


# ============================================================
# WEBHOOKS PAIEMENT EN LIGNE (appelés par les serveurs Orange/Wave,
# jamais par un navigateur : pas de session, pas de jeton CSRF)
#
# ⚠️ Vérification de l'authenticité des webhooks de paiement :
#
# - Wave documente officiellement un en-tête "Wave-Signature" (voir
#   https://docs.wave.com/webhook) : HMAC-SHA256(secret, horodatage +
#   corps_brut), avec rejet des requêtes trop anciennes (> 5 minutes).
#   C'est ce que _verifier_signature_wave() implémente ci-dessous.
#
# - Orange Money ne fournit pas de signature cryptographique publique
#   et documentée pour l'intégration utilisée ici. Pour ne pas inventer
#   un mécanisme de vérification non confirmé, l'URL du webhook Orange
#   est à la place protégée par un jeton secret inclus dans l'URL elle-
#   même (PAIEMENT_ORANGE_WEBHOOK_TOKEN) : seule la personne qui
#   configure l'URL de notification dans le back-office Orange connaît
#   cette URL. Si Orange publie un jour un mécanisme de signature
#   documenté pour ce produit, remplacer cette vérification par la
#   leur sera simple (un seul endroit à changer : paiement_webhook_orange).
#
# Aucun des deux mécanismes n'a pu être testé contre de vrais appels
# (aucun compte marchand réel disponible ici) : à vérifier en conditions
# réelles avant la mise en production.
# ============================================================

@csrf_exempt
@require_POST
def paiement_webhook_orange(request, jeton_secret):
    import hmac

    jeton_attendu = getattr(settings, 'PAIEMENT_ORANGE_WEBHOOK_TOKEN', '') or ''
    if not jeton_attendu or not hmac.compare_digest(jeton_secret, jeton_attendu):
        # Jeton absent de la configuration, ou jeton incorrect dans l'URL
        # appelée : on refuse plutôt que de faire confiance au corps de la
        # requête, Orange Money ne fournissant pas de signature vérifiable
        # pour cette intégration.
        return HttpResponse(status=403)
    return _traiter_webhook_paiement(request, "OM-")


@csrf_exempt
@require_POST
def paiement_webhook_wave(request):
    if not _verifier_signature_wave(request):
        return HttpResponse(status=403)
    return _traiter_webhook_paiement(request, "WAVE-")


def _verifier_signature_wave(request):
    """Vérifie l'en-tête Wave-Signature selon la documentation officielle
    (https://docs.wave.com/webhook) :
      - format "t=<horodatage>,v1=<signature hex>[,v1=<autre signature>...]"
      - signature attendue = HMAC-SHA256(secret, horodatage + corps_brut),
        encodée en hexadécimal
      - requête refusée si l'horodatage a plus de 5 minutes (anti-rejeu)
    """
    import hmac
    import hashlib
    import time

    secret = getattr(settings, 'PAIEMENT_WAVE_WEBHOOK_SECRET', '') or ''
    if not secret:
        return False

    en_tete = request.META.get('HTTP_WAVE_SIGNATURE', '')
    if not en_tete:
        return False

    horodatage = None
    signatures_recues = []
    for partie in en_tete.split(','):
        partie = partie.strip()
        if partie.startswith('t='):
            horodatage = partie[2:]
        elif partie.startswith('v1='):
            signatures_recues.append(partie[3:])

    if not horodatage or not signatures_recues:
        return False

    try:
        horodatage_int = int(horodatage)
    except ValueError:
        return False

    if abs(time.time() - horodatage_int) > 300:
        # Horodatage de plus de 5 minutes : requête trop ancienne, on
        # refuse par précaution contre une attaque par rejeu.
        return False

    corps_brut = request.body or b""
    message = (horodatage + corps_brut.decode('utf-8', errors='replace')).encode('utf-8')
    signature_calculee = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

    for signature in signatures_recues:
        if hmac.compare_digest(signature_calculee, signature):
            return True
    return False


def _traiter_webhook_paiement(request, prefixe_attendu):
    try:
        donnees = json.loads(request.body.decode() or "{}")
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    reference = donnees.get("order_id") or donnees.get("client_reference") or ""
    statut_recu = str(donnees.get("status", "")).upper()

    if not reference.startswith(prefixe_attendu):
        return HttpResponse(status=400)

    paiement = None
    try:
        paiement = Paiement.objects.get(reference_transaction=reference)
    except Paiement.DoesNotExist:
        return HttpResponse(status=404)

    if paiement.statut_paiement != 'EN_ATTENTE':
        # Déjà traité (webhook rejoué) : on répond OK sans rien refaire.
        return HttpResponse(status=200)

    if statut_recu in ("SUCCESS", "SUCCESSFUL", "CONFIRME", "PAID"):
        paiement.statut_paiement = 'CONFIRME'
    else:
        paiement.statut_paiement = 'ECHEC'
    paiement.save(update_fields=["statut_paiement"])

    return HttpResponse(status=200)


def verifier_recu(request):
    """
    Vérification publique d'authenticité d'un reçu de paiement (outil
    anti-fraude). N'importe qui peut saisir un numéro de reçu et obtenir
    une confirmation — mais SANS jamais révéler l'identité du payeur ni
    la parcelle concernée, uniquement : montant, date, type de taxe et
    mode de paiement. Même principe de confidentialité que la recherche
    cadastrale et la carte publique.
    """
    numero = request.GET.get("numero_recu", "").strip()
    paiement = None
    recherche_effectuee = bool(numero)

    if numero:
        paiement = (
            Paiement.objects
            .select_related("taxation", "taxation__type_taxe")
            .filter(numero_recu__iexact=numero, statut_paiement='CONFIRME')
            .first()
        )

    return render(request, "foncier/verifier_recu.html", {
        "numero": numero,
        "paiement": paiement,
        "recherche_effectuee": recherche_effectuee,
    })



def recherche_cadastrale(request):
    """
    Recherche cadastrale publique : n'importe qui peut chercher une parcelle
    par numéro NICAD, adresse/quartier ou nom de zone, et voir ses
    informations non nominatives (superficie, adresse, occupation du sol,
    zone). Aucune donnée fiscale ni le nom du propriétaire ne sont affichés
    ici — voir api_parcelles_geojson pour la même règle appliquée à la carte.
    """
    q = request.GET.get("q", "").strip()
    resultats = []

    if q:
        resultats = (
            Parcelle.objects.select_related("zone")
            .filter(
                Q(nicad__icontains=q)
                | Q(adresse_parcelle__icontains=q)
                | Q(zone__nom__icontains=q)
            )
            .only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "occupation_sol", "type_document", "zone__nom",
            )
            .order_by("nicad")[:50]
        )

    return render(request, "foncier/recherche_cadastrale.html", {
        "q": q,
        "resultats": resultats,
        "recherche_effectuee": bool(q),
    })


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
 
 
@receiver([post_save, post_delete], sender=Parcelle)
def _invalider_cache_parcelles(sender, **kwargs):
    cache.delete(CACHE_KEY_PUBLIC)
    cache.delete(CACHE_KEY_ADMIN)


from foncier.models import QuartierOfficiel, SectionCadastrale, LimiteAdministrative


@receiver([post_save, post_delete], sender=QuartierOfficiel)
def _invalider_cache_zones(sender, **kwargs):
    cache.delete(CACHE_KEY_ZONES)


@receiver([post_save, post_delete], sender=SectionCadastrale)
def _invalider_cache_sections(sender, **kwargs):
    cache.delete(CACHE_KEY_SECTIONS)


@receiver([post_save, post_delete], sender=LimiteAdministrative)
def _invalider_cache_limites(sender, **kwargs):
    cache.delete(CACHE_KEY_LIMITES)

@login_required
def recu_pdf_view(request, pk):
    """
    Génère un reçu de paiement officiel en PDF, téléchargeable par le
    citoyen propriétaire du paiement (via son ProfilCitoyen) ou par un
    agent (is_staff). Contrairement à la vérification publique de reçu
    (verifier_recu), ce document est privé et contient le nom du
    contribuable — d'où le contrôle d'accès strict.
    """
    paiement = get_object_or_404(
        Paiement.objects.select_related(
            "taxation", "taxation__contribuable", "taxation__type_taxe", "taxation__parcelle"
        ),
        pk=pk,
    )

    profil = getattr(request.user, "profil_citoyen", None)
    est_proprietaire = (
        profil is not None and profil.actif
        and profil.contribuable_id == paiement.taxation.contribuable_id
    )
    if not (request.user.is_staff or est_proprietaire):
        raise PermissionDenied("Vous n'avez pas accès à ce reçu.")

    if paiement.statut_paiement != 'CONFIRME':
        raise PermissionDenied("Ce paiement n'est pas encore confirmé, aucun reçu n'est disponible.")

    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.colors import HexColor

    VERT_FONCE = HexColor("#3c2a20")
    OR = HexColor("#c9982e")
    GRIS = HexColor("#6b5d4f")
    BORDURE = HexColor("#e6e0d4")

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4
    marge = 20 * mm

    # --- En-tête ---
    c.setFillColor(VERT_FONCE)
    c.rect(0, hauteur - 32 * mm, largeur, 32 * mm, fill=True, stroke=False)
    c.setFillColor(OR)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(marge, hauteur - 16 * mm, "KEUR MASSAR NORD")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 10)
    c.drawString(marge, hauteur - 23 * mm, "Commune de Keur Massar Nord — Foncier & Fiscal")

    c.setFillColor(OR)
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(largeur - marge, hauteur - 16 * mm, "REÇU DE PAIEMENT")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 10)
    c.drawRightString(largeur - marge, hauteur - 23 * mm, paiement.numero_recu)

    y = hauteur - 46 * mm

    # --- Bloc contribuable ---
    contribuable = paiement.taxation.contribuable
    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "CONTRIBUABLE")
    y -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge, y, f"{contribuable.nom} {contribuable.prenom}")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"Identifiant fiscalité : {contribuable.numero_fiscal}")

    y -= 14 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 10 * mm

    # --- Détails du paiement (tableau simple) ---
    lignes = [
        ("Taxe concernée", f"{paiement.taxation.type_taxe.libelle} ({paiement.taxation.annee_fiscale})"),
        ("Parcelle", paiement.taxation.parcelle.nicad if paiement.taxation.parcelle_id else "—"),
        ("Date de paiement", paiement.date_paiement.strftime("%d/%m/%Y")),
        ("Mode de paiement", paiement.get_mode_paiement_display()),
    ]
    for label, valeur in lignes:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 10)
        c.drawString(marge, y, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(largeur - marge, y, str(valeur))
        y -= 8 * mm

    y -= 6 * mm
    c.setFillColor(OR)
    c.rect(marge, y - 4 * mm, largeur - 2 * marge, 18 * mm, fill=True, stroke=False)
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(marge + 6 * mm, y + 6 * mm, "MONTANT PAYÉ")
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(largeur - marge - 6 * mm, y + 5 * mm, f"{paiement.montant:,.0f} FCFA".replace(",", " "))

    # --- Pied de page ---
    c.setFillColor(GRIS)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        marge, 18 * mm,
        "Document généré électroniquement. Son authenticité peut être vérifiée sur "
        "keurmassarnord.sn/fiscalite/verifier-recu/"
    )
    c.drawString(marge, 13 * mm, f"Édité le {paiement.date_paiement.today().strftime('%d/%m/%Y')} depuis l'espace citoyen KEUR MASSAR NORD.")

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="recu_{paiement.numero_recu}.pdf"'
    return response


def actualites_liste(request):
    """
    Page publique listant TOUTES les actualités publiées (contrairement à
    l'accueil qui n'en montre que 3), avec recherche par mot-clé et
    filtre par catégorie, paginée.
    """
    q = request.GET.get("q", "").strip()
    categorie = request.GET.get("categorie", "").strip()

    actualites = Actualite.objects.filter(publie=True)

    if q:
        actualites = actualites.filter(
            Q(titre__icontains=q) | Q(chapo__icontains=q) | Q(contenu__icontains=q)
        )
    if categorie:
        actualites = actualites.filter(categorie=categorie)

    actualites = actualites.order_by("-date_publication", "-date_creation")

    paginator = Paginator(actualites, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "foncier/actualites_liste.html", {
        "page_obj": page_obj,
        "q": q,
        "categorie": categorie,
        "categories": Actualite.CATEGORIES,
    })


def actualite_detail(request, pk):
    """Page de détail d'une actualité publiée."""
    actualite = get_object_or_404(Actualite, pk=pk, publie=True)

    autres = (
        Actualite.objects.filter(publie=True)
        .exclude(pk=actualite.pk)
        .order_by("-date_publication")[:3]
    )

    return render(request, "foncier/actualite_detail.html", {
        "actualite": actualite,
        "autres": autres,
    })

def api_parcelles_bounds(request):
    """
    Renvoie l'enveloppe geographique (bounding box) de TOUTES les
    parcelles, calculee cote base de donnees (tres rapide, une seule
    requete d'agregation). Utilisee par la carte pour se cadrer
    automatiquement sur tout le territoire des l'ouverture, quelle que
    soit la taille de l'ecran -- garantit qu'on ne "rate" jamais une
    partie de la commune au chargement initial.
    """
    from django.contrib.gis.db.models import Extent

    resultat = Parcelle.objects.exclude(geom__isnull=True).aggregate(etendue=Extent("geom"))
    etendue = resultat["etendue"]
    if not etendue:
        return JsonResponse({"ok": False})
    west, south, east, north = etendue
    return JsonResponse({"ok": True, "west": west, "south": south, "east": east, "north": north})


# ============================================================
# DOCUMENTS OFFICIELS (quitus fiscal, attestation de non-imposition) —
# meme style visuel que le recu de paiement (recu_pdf_view), genere en
# PDF avec reportlab. Principe SenTax : ces documents ne sont delivres
# que si la situation fiscale du contribuable le permet reellement.
# ============================================================

def _preparer_pdf_document(titre_document, numero_reference):
    """Cree le canvas ReportLab et dessine l'en-tete commun (bande verte,
    logo texte, titre du document). Renvoie (buffer, canvas, largeur,
    hauteur, marge, y_depart, couleurs)."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.colors import HexColor

    VERT_FONCE = HexColor("#3c2a20")
    OR = HexColor("#c9982e")
    GRIS = HexColor("#6b5d4f")
    BORDURE = HexColor("#e6e0d4")

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4
    marge = 20 * mm

    c.setFillColor(VERT_FONCE)
    c.rect(0, hauteur - 32 * mm, largeur, 32 * mm, fill=True, stroke=False)
    c.setFillColor(OR)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(marge, hauteur - 16 * mm, "KEUR MASSAR NORD")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 10)
    c.drawString(marge, hauteur - 23 * mm, "Commune de Keur Massar Nord — Foncier & Fiscal")

    c.setFillColor(OR)
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(largeur - marge, hauteur - 16 * mm, titre_document)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 10)
    c.drawRightString(largeur - marge, hauteur - 23 * mm, numero_reference)

    return buffer, c, largeur, hauteur, marge, hauteur - 46 * mm, (VERT_FONCE, OR, GRIS, BORDURE)


def _pied_de_page_document(c, marge, hauteur_page_url, texte_verif):
    """Pied de page commun (authenticite + date d'edition)."""
    from django.utils import timezone
    from reportlab.lib.colors import HexColor
    c.setFillColor(HexColor("#6b5d4f"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(marge, 18 * 2.834645669, texte_verif)
    c.drawString(marge, 13 * 2.834645669, f"Édité le {timezone.now().strftime('%d/%m/%Y')} depuis l'espace citoyen KEUR MASSAR NORD.")


@login_required
def quitus_fiscal_pdf_view(request):
    """
    Genere un QUITUS FISCAL en PDF : atteste que le contribuable est a
    jour de ses obligations fiscales communales. Refuse de le delivrer
    si ce n'est reellement pas le cas (document a valeur officielle).
    """
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    contribuable = profil.contribuable
    if contribuable.statut_global != "A_JOUR":
        messages.error(
            request,
            "Un quitus fiscal ne peut être délivré que si votre compte est à jour de tous vos paiements. "
            "Réglez vos taxations en retard puis réessayez."
        )
        return redirect("citoyen_espace")

    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor

    numero_doc = f"QF-{contribuable.numero_fiscal}-{timezone_now_str()}"
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "QUITUS FISCAL", numero_doc
    )

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "CONTRIBUABLE")
    y -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge, y, f"{contribuable.nom} {contribuable.prenom}")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"Identifiant fiscalité : {contribuable.numero_fiscal}")

    y -= 14 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 12 * mm

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 11)
    texte = (
        f"La commune de Keur Massar Nord atteste par le présent document que "
        f"{contribuable.nom} {contribuable.prenom} est, à la date d'édition, "
        f"À JOUR de l'ensemble de ses obligations fiscales communales "
        f"(taxes foncières sur les propriétés bâties et non bâties)."
    )
    from textwrap import wrap
    for ligne in wrap(texte, width=78):
        c.drawString(marge, y, ligne)
        y -= 6 * mm

    y -= 8 * mm
    c.setFillColor(OR)
    c.rect(marge, y - 4 * mm, largeur - 2 * marge, 18 * mm, fill=True, stroke=False)
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(marge + 6 * mm, y + 6 * mm, "TOTAL RÉGLÉ")
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(
        largeur - marge - 6 * mm, y + 5 * mm,
        f"{contribuable.montant_paye_total:,.0f} FCFA".replace(",", " ")
    )

    _pied_de_page_document(
        c, marge, hauteur,
        "Document généré électroniquement, à valeur informative. Son authenticité peut être "
        "vérifiée auprès des services fiscaux de la commune."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="quitus_fiscal_{contribuable.numero_fiscal}.pdf"'
    return response


@login_required
def attestation_non_imposition_pdf_view(request):
    """
    Genere une ATTESTATION DE NON-IMPOSITION en PDF : atteste que le
    contribuable n'est redevable d'aucune taxe communale. Refuse de la
    delivrer si le contribuable a bien des taxes dues (meme partiellement
    payees) — ce document a une signification precise, differente d'un
    simple "compte a jour".
    """
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    contribuable = profil.contribuable
    if contribuable.montant_du_total and contribuable.montant_du_total > 0:
        messages.error(
            request,
            "Une attestation de non-imposition ne peut être délivrée qu'aux contribuables "
            "n'ayant aucune taxe communale à leur nom. Votre dossier comporte des taxations : "
            "un quitus fiscal peut être demandé une fois vos paiements à jour."
        )
        return redirect("citoyen_espace")

    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from textwrap import wrap

    numero_doc = f"ANI-{contribuable.numero_fiscal}-{timezone_now_str()}"
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "ATTESTATION DE NON-IMPOSITION", numero_doc
    )

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "CONTRIBUABLE")
    y -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge, y, f"{contribuable.nom} {contribuable.prenom}")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"Identifiant fiscalité : {contribuable.numero_fiscal}")

    y -= 14 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 12 * mm

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 11)
    texte = (
        f"La commune de Keur Massar Nord atteste par le présent document que "
        f"{contribuable.nom} {contribuable.prenom} n'est, à la date d'édition, "
        f"redevable d'AUCUNE taxe foncière communale (CFPB/CFPNB) sur le territoire "
        f"de la commune."
    )
    for ligne in wrap(texte, width=78):
        c.drawString(marge, y, ligne)
        y -= 6 * mm

    _pied_de_page_document(
        c, marge, hauteur,
        "Document généré électroniquement, à valeur informative. Son authenticité peut être "
        "vérifiée auprès des services fiscaux de la commune."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="attestation_non_imposition_{contribuable.numero_fiscal}.pdf"'
    return response


def timezone_now_str():
    from django.utils import timezone
    return timezone.now().strftime("%Y%m%d")


def immatriculation_demande_view(request):
    """
    Formulaire PUBLIC (aucun compte requis) permettant a une personne
    qui n'a jamais ete contribuable de demander sa premiere
    immatriculation fiscale, pour une parcelle deja cadastree mais pas
    encore rattachee a un proprietaire/contribuable connu.
    """
    if request.method == "POST":
        form = DemandeImmatriculationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Votre demande a bien été soumise. Un agent l'examinera et vous "
                "recevrez votre numéro fiscal par email une fois votre dossier validé."
            )
            return redirect("immatriculation_demande")
    else:
        form = DemandeImmatriculationForm()

    return render(request, "foncier/immatriculation_demande.html", {
        "form": form,
    })


def mutation_demande_view(request):
    """
    Formulaire PUBLIC (aucun compte requis) permettant a l'acheteur
    d'une parcelle deja immatriculee de demander le transfert du
    dossier fiscal a son nom (mutation fiscale suite a une revente).
    """
    if request.method == "POST":
        form = DemandeMutationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Votre demande de mutation a bien été soumise. Un agent l'examinera et vous "
                "recevrez votre numéro fiscal par email une fois votre dossier validé."
            )
            return redirect("mutation_demande")
    else:
        form = DemandeMutationForm()

    return render(request, "foncier/mutation_demande.html", {
        "form": form,
    })


@login_required
def releve_compte_pdf_view(request):
    """
    Genere un RELEVE DE COMPTE FISCAL en PDF : recapitulatif de TOUTES
    les taxations du contribuable, toutes annees confondues (pas
    seulement un recu de paiement unique). Reprend le meme style
    visuel que les autres documents (quitus, attestation).
    """
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from foncier.models import Taxation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    contribuable = profil.contribuable
    taxations = (
        Taxation.objects.filter(contribuable=contribuable)
        .select_related("type_taxe", "parcelle")
        .order_by("-annee_fiscale")
    )

    numero_doc = f"RC-{contribuable.numero_fiscal}-{timezone_now_str()}"
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "RELEVÉ DE COMPTE", numero_doc
    )

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "CONTRIBUABLE")
    y -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge, y, f"{contribuable.nom} {contribuable.prenom}")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"Identifiant fiscalité : {contribuable.numero_fiscal}")

    y -= 12 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 10 * mm

    # --- En-tete du tableau ---
    def dessiner_entete_tableau(y_pos):
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(marge, y_pos, "ANNÉE")
        c.drawString(marge + 22 * mm, y_pos, "TAXE")
        c.drawString(marge + 70 * mm, y_pos, "PARCELLE")
        c.drawRightString(marge + 122 * mm, y_pos, "DÛ")
        c.drawRightString(marge + 145 * mm, y_pos, "PAYÉ")
        c.drawRightString(largeur - marge, y_pos, "STATUT")
        y_pos -= 4 * mm
        c.setStrokeColor(BORDURE)
        c.line(marge, y_pos, largeur - marge, y_pos)
        return y_pos - 6 * mm

    y = dessiner_entete_tableau(y)

    total_du = Decimal("0")
    total_paye = Decimal("0")

    for t in taxations:
        if y < 30 * mm:
            # Page pleine : nouvelle page, redessine l'en-tete
            _pied_de_page_document(
                c, marge, hauteur,
                "Document généré électroniquement, à valeur informative."
            )
            c.showPage()
            c.setFillColor(VERT_FONCE)
            y = hauteur - 20 * mm
            y = dessiner_entete_tableau(y)

        statut_label = "À jour" if t.statut == "A_JOUR" else "En retard"
        parcelle_label = t.parcelle.nicad if t.parcelle_id else "—"

        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica", 8.5)
        c.drawString(marge, y, str(t.annee_fiscale))
        c.drawString(marge + 22 * mm, y, t.type_taxe.libelle[:28])
        c.drawString(marge + 70 * mm, y, parcelle_label[:20])
        c.drawRightString(marge + 122 * mm, y, f"{t.montant_du:,.0f}".replace(",", " "))
        c.drawRightString(marge + 145 * mm, y, f"{t.montant_paye:,.0f}".replace(",", " "))
        c.setFillColor(HexColor("#2f7a4f") if t.statut == "A_JOUR" else HexColor("#b23b2e"))
        c.drawRightString(largeur - marge, y, statut_label)

        total_du += t.montant_du
        total_paye += t.montant_paye
        y -= 7 * mm

    y -= 6 * mm
    c.setFillColor(OR)
    c.rect(marge, y - 4 * mm, largeur - 2 * marge, 18 * mm, fill=True, stroke=False)
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(marge + 6 * mm, y + 7 * mm, "TOTAL DÛ (toutes années)")
    c.drawString(marge + 6 * mm, y + 1 * mm, "TOTAL RÉGLÉ (toutes années)")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(largeur - marge - 6 * mm, y + 7 * mm, f"{total_du:,.0f} FCFA".replace(",", " "))
    c.drawRightString(largeur - marge - 6 * mm, y + 1 * mm, f"{total_paye:,.0f} FCFA".replace(",", " "))

    _pied_de_page_document(
        c, marge, hauteur,
        "Document généré électroniquement, à valeur informative. Son authenticité peut être "
        "vérifiée auprès des services fiscaux de la commune."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="releve_compte_{contribuable.numero_fiscal}.pdf"'
    return response


def _wgs84_to_utm28n(lon, lat):
    """Convertit des coordonnees WGS84 (degres) en coordonnees UTM Zone
    28N (metres), la projection utilisee au Senegal. Formule standard
    de Snyder, implementee ici pour ne pas dependre de pyproj/GDAL."""
    import math

    a = 6378137.0
    f = 1 / 298.257223563
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    k0 = 0.9996
    lon0 = math.radians(-15.0)

    phi = math.radians(lat)
    lam = math.radians(lon)

    n = a / math.sqrt(1 - e2 * math.sin(phi) ** 2)
    t = math.tan(phi) ** 2
    cc = ep2 * math.cos(phi) ** 2
    aa = math.cos(phi) * (lam - lon0)

    m = a * (
        (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256) * phi
        - (3 * e2 / 8 + 3 * e2 ** 2 / 32 + 45 * e2 ** 3 / 1024) * math.sin(2 * phi)
        + (15 * e2 ** 2 / 256 + 45 * e2 ** 3 / 1024) * math.sin(4 * phi)
        - (35 * e2 ** 3 / 3072) * math.sin(6 * phi)
    )

    x = k0 * n * (
        aa + (1 - t + cc) * aa ** 3 / 6
        + (5 - 18 * t + t ** 2 + 72 * cc - 58 * ep2) * aa ** 5 / 120
    ) + 500000.0

    y = k0 * (
        m + n * math.tan(phi) * (
            aa ** 2 / 2 + (5 - t + 9 * cc + 4 * cc ** 2) * aa ** 4 / 24
            + (61 - 58 * t + t ** 2 + 600 * cc - 330 * ep2) * aa ** 6 / 720
        )
    )
    return x, y


def _anneau_exterieur_utm(polygone):
    """Sommets (x, y) en UTM 28N de l'anneau exterieur d'un Polygon
    GEOS, sans le point de fermeture duplique."""
    coords = list(polygone.exterior_ring.coords)
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]
    return [_wgs84_to_utm28n(lon, lat) for lon, lat in coords]


def _sommets_parcelle_utm(parcelle):
    polygone = parcelle.geom[0]
    return _anneau_exterieur_utm(polygone)


def _voisines_parcelle(parcelle, max_resultats=30):
    """Vraies parcelles voisines de `parcelle`, trouvees par
    intersection spatiale reelle via PostGIS (index spatial, donc
    rapide meme sur des dizaines de milliers de parcelles). Le rayon
    de recherche s'adapte a la taille de la parcelle : une tres grande
    parcelle regarde plus loin pour trouver du contexte autour d'elle."""
    from .models import Parcelle

    xmin, ymin, xmax, ymax = parcelle.geom.extent
    x1, y1 = _wgs84_to_utm28n(xmin, ymin)
    x2, y2 = _wgs84_to_utm28n(xmax, ymax)
    largeur_m = abs(x2 - x1)
    hauteur_m = abs(y2 - y1)
    rayon_m = max(60.0, 0.55 * max(largeur_m, hauteur_m))
    rayon_m = min(rayon_m, 350.0)
    tampon_deg = rayon_m / 111320.0

    try:
        zone_recherche = parcelle.geom.buffer(tampon_deg)
        voisines = list(
            Parcelle.objects.filter(geom__intersects=zone_recherche)
            .exclude(pk=parcelle.pk)
            .only("id", "nicad", "numero_parcelle", "geom")[:max_resultats]
        )
    except Exception:
        voisines = []
    return voisines


def _texte_pdf(valeur, max_longueur=60):
    """Nettoie une valeur avant de l'ecrire dans le PDF : retire les
    caracteres non imprimables issus de donnees importees (shapefile,
    saisie libre) qui corrompraient l'affichage."""
    if valeur in (None, ""):
        return "-"
    texte = str(valeur)
    accents_ok = "\u00e0\u00e2\u00e4\u00e9\u00e8\u00ea\u00eb\u00ee\u00ef\u00f4\u00f6\u00f9\u00fb\u00fc\u00e7\u00c0\u00c2\u00c4\u00c9\u00c8\u00ca\u00cb\u00ce\u00cf\u00d4\u00d6\u00d9\u00db\u00dc\u00c7\u00b0\u00b2"
    propre = []
    for ch in texte:
        if 32 <= ord(ch) <= 126 or ch in accents_ok:
            propre.append(ch)
    texte = "".join(propre).strip()
    return texte[:max_longueur] if texte else "-"


def _pas_grille_adapte(etendue_m):
    for pas in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if etendue_m / pas <= 8:
            return pas
    return 2000


def _generer_image_plan_situation(parcelle, voisines, taille_px=1200):
    """Dessine le plan de situation (parcelle + voisines + grille +
    fleche nord) en PNG via Pillow et renvoie un buffer pret a etre
    insere dans le PDF. Le cadrage est fixe sur la parcelle principale
    (zoom coherent) : seules les voisines qui tombent dans ce cadrage
    sont affichees, pour eviter qu'un groupe de parcelles eloignees
    n'oblige a tout dezoomer."""
    import io as io_module
    import math
    from PIL import Image, ImageDraw, ImageFont

    sommets_principal = _sommets_parcelle_utm(parcelle)

    xs_p = [p[0] for p in sommets_principal]
    ys_p = [p[1] for p in sommets_principal]
    largeur_principale = max(xs_p) - min(xs_p)
    hauteur_principale = max(ys_p) - min(ys_p)
    cx = (max(xs_p) + min(xs_p)) / 2
    cy = (max(ys_p) + min(ys_p)) / 2

    etendue = max(largeur_principale, hauteur_principale, 25.0) * 2.1 + 25.0
    xmin, xmax = cx - etendue / 2, cx + etendue / 2
    ymin, ymax = cy - etendue / 2, cy + etendue / 2

    polygones_voisins = []
    for voisine in voisines:
        try:
            pts = _anneau_exterieur_utm(voisine.geom[0])
        except Exception:
            continue
        if not pts:
            continue
        vxmin = min(p[0] for p in pts)
        vxmax = max(p[0] for p in pts)
        vymin = min(p[1] for p in pts)
        vymax = max(p[1] for p in pts)
        chevauche = not (vxmax < xmin or vxmin > xmax or vymax < ymin or vymin > ymax)
        if chevauche:
            polygones_voisins.append((voisine, pts))

    marge_cadre = int(taille_px * 0.075)
    zone_dessin = taille_px - 2 * marge_cadre
    echelle = zone_dessin / etendue

    def vers_px(point_x, point_y):
        px = marge_cadre + (point_x - xmin) * echelle
        py = taille_px - marge_cadre - (point_y - ymin) * echelle
        return (px, py)

    img = Image.new("RGB", (taille_px, taille_px), "white")
    draw = ImageDraw.Draw(img)

    try:
        police_grille = ImageFont.load_default(size=18)
        police_label = ImageFont.load_default(size=22)
        police_num = ImageFont.load_default(size=28)
    except TypeError:
        police_grille = police_label = police_num = ImageFont.load_default()

    pas = _pas_grille_adapte(etendue)
    valeur = math.floor(xmin / pas) * pas
    while valeur <= xmax:
        p1 = vers_px(valeur, ymin)
        p2 = vers_px(valeur, ymax)
        draw.line([p1, p2], fill=(215, 215, 215), width=1)
        etiquette = "{:,.0f}".format(valeur).replace(",", " ")
        draw.text((p1[0], taille_px - marge_cadre + 14), etiquette, fill=(100, 100, 100), font=police_grille, anchor="mt")
        draw.text((p1[0], marge_cadre - 14), etiquette, fill=(100, 100, 100), font=police_grille, anchor="mb")
        valeur += pas

    valeur = math.floor(ymin / pas) * pas
    while valeur <= ymax:
        p1 = vers_px(xmin, valeur)
        p2 = vers_px(xmax, valeur)
        draw.line([p1, p2], fill=(215, 215, 215), width=1)
        etiquette = "{:,.0f}".format(valeur).replace(",", " ")
        draw.text((marge_cadre - 10, p1[1]), etiquette, fill=(100, 100, 100), font=police_grille, anchor="rm")
        draw.text((taille_px - marge_cadre + 10, p1[1]), etiquette, fill=(100, 100, 100), font=police_grille, anchor="lm")
        valeur += pas

    draw.rectangle(
        [marge_cadre, marge_cadre, taille_px - marge_cadre, taille_px - marge_cadre],
        outline=(60, 60, 60), width=2,
    )

    for voisine, pts in polygones_voisins:
        pts_px = [vers_px(px, py) for px, py in pts]
        if len(pts_px) >= 2:
            draw.polygon(pts_px, fill=(238, 218, 178), outline=(201, 138, 46), width=2)
            centre_x = sum(p[0] for p in pts_px) / len(pts_px)
            centre_y = sum(p[1] for p in pts_px) / len(pts_px)
            if marge_cadre < centre_x < taille_px - marge_cadre and marge_cadre < centre_y < taille_px - marge_cadre:
                etiquette = voisine.numero_parcelle or voisine.nicad[-4:]
                draw.text((centre_x, centre_y), str(etiquette), fill=(90, 60, 20), font=police_label, anchor="mm")

    pts_px = [vers_px(px, py) for px, py in sommets_principal]
    if len(pts_px) >= 2:
        draw.polygon(pts_px, fill=(250, 210, 200), outline=(195, 30, 30), width=5)
        centre_x = sum(p[0] for p in pts_px) / len(pts_px)
        centre_y = sum(p[1] for p in pts_px) / len(pts_px)
        etiquette_principale = parcelle.numero_parcelle or parcelle.nicad[-4:]
        draw.text((centre_x, centre_y), str(etiquette_principale), fill=(175, 20, 20), font=police_num, anchor="mm")

    nx = taille_px - marge_cadre - 55
    ny = marge_cadre + 90
    draw.line([(nx, ny + 50), (nx, ny - 30)], fill=(25, 25, 25), width=4)
    draw.polygon([(nx, ny - 48), (nx - 14, ny - 18), (nx + 14, ny - 18)], fill=(25, 25, 25))
    draw.text((nx, ny - 62), "N", fill=(25, 25, 25), font=police_num, anchor="mm")

    tampon = io_module.BytesIO()
    img.save(tampon, format="PNG")
    tampon.seek(0)
    return tampon


def _dessiner_cadre_titre(c, x, y_haut, largeur, hauteur, titre, couleur_texte, couleur_bordure, couleur_bandeau):
    """Cadre avec bandeau de titre en haut (comme les rubriques d'un
    extrait cadastral officiel). Renvoie le y de depart du contenu."""
    from reportlab.lib.units import mm

    bandeau = 6 * mm
    c.setStrokeColor(couleur_bordure)
    c.setLineWidth(0.6)
    c.rect(x, y_haut - hauteur, largeur, hauteur, fill=False, stroke=True)
    c.setFillColor(couleur_bandeau)
    c.rect(x, y_haut - bandeau, largeur, bandeau, fill=True, stroke=False)
    c.setStrokeColor(couleur_bordure)
    c.line(x, y_haut - bandeau, x + largeur, y_haut - bandeau)
    c.setFillColor(couleur_texte)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 2 * mm, y_haut - bandeau + 1.8 * mm, titre)
    return y_haut - bandeau - 5 * mm


@login_required
def extrait_cadastral_pdf_view(request, pk):
    """
    Genere l'extrait de plan foncier officiel en PDF pour une demande de
    service PRETE et payee (si payante) : localisation, proprietaire,
    identification du titre, plan de situation avec grille de
    coordonnees UTM Zone 28N, tableau des sommets et legende.
    """
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    from .models import DemandeService

    demande = get_object_or_404(DemandeService, pk=pk, demandeur=request.user)

    if demande.statut != "PRETE":
        messages.error(request, "Ce document n'est pas encore pret.")
        return redirect("citoyen_demande_detail", pk=pk)

    if demande.type_demande.tarif and demande.type_demande.tarif > 0 and demande.statut_paiement != "CONFIRME":
        messages.error(
            request,
            "Le paiement de cette demarche doit d'abord etre valide avant de pouvoir telecharger le document."
        )
        return redirect("citoyen_demande_detail", pk=pk)

    parcelle = demande.parcelle
    if parcelle is None:
        messages.error(request, "Aucune parcelle n'est associee a cette demarche.")
        return redirect("citoyen_demande_detail", pk=pk)

    numero_doc = "EPF-{}".format(demande.numero_dossier)
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "EXTRAIT DE PLAN FONCIER", numero_doc
    )

    largeur_contenu = largeur - 2 * marge
    BANDEAU_CLAIR = HexColor("#f2ede1")

    titre_foncier = parcelle.numero_titre_foncier or parcelle.nicad
    section_label = parcelle.section_cadastrale or "-"
    parcelle_label = parcelle.numero_parcelle or parcelle.nicad

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, "TITRE / REFERENCE : {}".format(titre_foncier))
    c.setFont("Helvetica", 9)
    c.drawRightString(
        largeur - marge, y,
        "Section : {}    Parcelle : {}".format(section_label, parcelle_label)
    )
    y -= 6 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 7 * mm

    largeur_col = (largeur_contenu - 6 * mm) / 2
    hauteur_rangee1 = 32 * mm
    x_gauche = marge
    x_droite = marge + largeur_col + 6 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_col, hauteur_rangee1,
        "LOCALISATION DE LA PARCELLE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    quartier = parcelle.adresse_parcelle or (parcelle.zone.nom if parcelle.zone_id else "-")
    champs_localisation = [
        ("Region", "DAKAR"),
        ("Departement", "KEUR MASSAR"),
        ("Commune", "KEUR MASSAR NORD"),
        ("Quartier / Secteur", quartier),
    ]
    yc = y_contenu
    for label, valeur in champs_localisation:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_gauche + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_gauche + largeur_col - 2 * mm, yc, _texte_pdf(valeur, 40))
        yc -= 5.2 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_droite, y, largeur_col, hauteur_rangee1,
        "PROPRIETAIRE(S)", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    if parcelle.proprietaire_id:
        nom_complet = "{} {}".format(parcelle.proprietaire.nom, parcelle.proprietaire.prenom)
        cni = parcelle.proprietaire.ni_cni or "-"
        domicile = parcelle.proprietaire.adresse or "-"
    else:
        nom_complet = "Non renseigne"
        cni = "-"
        domicile = "-"
    champs_proprietaire = [
        ("Nom et prenoms", nom_complet),
        ("N de CNI", cni),
        ("Domicile", domicile),
    ]
    yc = y_contenu
    for label, valeur in champs_proprietaire:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_droite + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_droite + largeur_col - 2 * mm, yc, _texte_pdf(valeur, 36))
        yc -= 5.2 * mm

    y -= hauteur_rangee1 + 4 * mm

    hauteur_rangee2 = 32 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_col, hauteur_rangee2,
        "IDENTIFICATION DU TITRE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    champs_identification = [
        ("Titre foncier n", titre_foncier),
        ("Section cadastrale", section_label),
        ("N de parcelle", parcelle_label),
        ("Contenance", "{:,.0f} m2".format(parcelle.superficie).replace(",", " ") if parcelle.superficie else "-"),
    ]
    yc = y_contenu
    for label, valeur in champs_identification:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_gauche + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_gauche + largeur_col - 2 * mm, yc, _texte_pdf(valeur, 40))
        yc -= 5.2 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_droite, y, largeur_col, hauteur_rangee2,
        "NATURE DE LA PROPRIETE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    champs_nature = [
        ("Nature du document", parcelle.get_type_document_display()),
        ("Usage / Occupation", parcelle.occupation_sol or "-"),
        ("Statut fiscal", parcelle.get_statut_fiscal_display()),
        ("Zone", parcelle.zone.nom if parcelle.zone_id else "-"),
    ]
    yc = y_contenu
    for label, valeur in champs_nature:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 8)
        c.drawString(x_droite + 2 * mm, yc, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x_droite + largeur_col - 2 * mm, yc, _texte_pdf(valeur, 36))
        yc -= 5.2 * mm

    y -= hauteur_rangee2 + 4 * mm

    hauteur_plan = 95 * mm
    largeur_plan = 100 * mm
    largeur_colonne_droite = largeur_contenu - largeur_plan - 6 * mm
    x_colonne_droite = marge + largeur_plan + 6 * mm

    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_plan, hauteur_plan,
        "PLAN DE SITUATION", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )

    sommets = []
    try:
        voisines = _voisines_parcelle(parcelle)
        image_plan = _generer_image_plan_situation(parcelle, voisines)
        taille_image = min(largeur_plan - 4 * mm, hauteur_plan - 9 * mm)
        c.drawImage(
            ImageReader(image_plan),
            x_gauche + (largeur_plan - taille_image) / 2,
            y - 4 * mm - taille_image,
            width=taille_image, height=taille_image,
            preserveAspectRatio=True, mask="auto",
        )
        sommets = _sommets_parcelle_utm(parcelle)
    except Exception:
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(x_gauche + largeur_plan / 2, y - 40 * mm, "Plan non disponible pour cette parcelle.")

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Oblique", 6.5)
    c.drawCentredString(x_gauche + largeur_plan / 2, y - hauteur_plan + 3 * mm, "Systeme : WGS 84 / UTM Zone 28N - echelle approximative")

    hauteur_coord = 56 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_colonne_droite, y, largeur_colonne_droite, hauteur_coord,
        "COORDONNEES (UTM 28N)", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x_colonne_droite + 2 * mm, y_contenu, "Sommet")
    c.drawRightString(x_colonne_droite + largeur_colonne_droite * 0.6, y_contenu, "X (m)")
    c.drawRightString(x_colonne_droite + largeur_colonne_droite - 2 * mm, y_contenu, "Y (m)")
    yc = y_contenu - 4.5 * mm
    sommets_affiches = sommets[:8]
    for indice, (sx, sy) in enumerate(sommets_affiches, 1):
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica", 7.2)
        c.drawString(x_colonne_droite + 2 * mm, yc, "P{}".format(indice))
        c.drawRightString(x_colonne_droite + largeur_colonne_droite * 0.6, yc, "{:,.2f}".format(sx).replace(",", " "))
        c.drawRightString(x_colonne_droite + largeur_colonne_droite - 2 * mm, yc, "{:,.2f}".format(sy).replace(",", " "))
        yc -= 4.6 * mm
    if len(sommets) > 8:
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(x_colonne_droite + 2 * mm, yc, "+ {} sommet(s) supplementaire(s)".format(len(sommets) - 8))

    y_legende = y - hauteur_coord - 4 * mm
    hauteur_legende = hauteur_plan - hauteur_coord - 4 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_colonne_droite, y_legende, largeur_colonne_droite, hauteur_legende,
        "LEGENDE", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    yc = y_contenu
    c.setStrokeColor(HexColor("#c31e1e"))
    c.setLineWidth(2)
    c.rect(x_colonne_droite + 2 * mm, yc - 2.2 * mm, 6 * mm, 3 * mm, fill=False, stroke=True)
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 7)
    c.drawString(x_colonne_droite + 10 * mm, yc - 2 * mm, "Limite de la parcelle")
    yc -= 6 * mm
    c.setStrokeColor(HexColor("#5a5a5a"))
    c.setLineWidth(1)
    c.rect(x_colonne_droite + 2 * mm, yc - 2.2 * mm, 6 * mm, 3 * mm, fill=False, stroke=True)
    c.setFillColor(VERT_FONCE)
    c.drawString(x_colonne_droite + 10 * mm, yc - 2 * mm, "Limite de parcelle voisine")
    yc -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.drawString(x_colonne_droite + 2 * mm, yc - 2 * mm, "N = orientation Nord (haut du plan)")

    y -= hauteur_plan + 4 * mm

    hauteur_notes = 20 * mm
    y_contenu = _dessiner_cadre_titre(
        c, x_gauche, y, largeur_contenu, hauteur_notes,
        "NOTES", VERT_FONCE, BORDURE, BANDEAU_CLAIR,
    )
    notes = [
        "- Ce plan est un extrait du plan cadastral. Il ne constitue pas, a lui seul, un titre de propriete.",
        "- Les limites de la parcelle figurant sur ce plan sont donnees a titre indicatif.",
        "- Toute modification doit faire l'objet d'une mise a jour aupres du service du Cadastre de la commune.",
    ]
    yc = y_contenu
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 7.5)
    for ligne in notes:
        c.drawString(x_gauche + 2 * mm, yc, ligne)
        yc -= 4.3 * mm

    y -= hauteur_notes + 6 * mm

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_gauche, y, "LE CHEF DU SERVICE DU CADASTRE")
    c.drawString(x_droite, y, "VU ET CERTIFIE CONFORME")
    y -= 10 * mm
    c.setStrokeColor(BORDURE)
    c.setFont("Helvetica", 7)
    c.setFillColor(GRIS)
    c.line(x_gauche, y, x_gauche + largeur_col - 10 * mm, y)
    c.line(x_droite, y, x_droite + largeur_col - 10 * mm, y)
    c.drawString(x_gauche, y - 4 * mm, "Nom, date et signature")
    c.drawString(x_droite, y - 4 * mm, "Le Directeur du Cadastre")

    _pied_de_page_document(
        c, marge, hauteur,
        "Extrait de plan foncier delivre a titre informatif. Son authenticite peut etre "
        "verifiee aupres des services du cadastre de la commune de Keur Massar Nord."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="extrait_plan_foncier_{}.pdf"'.format(parcelle.nicad)
    return response
