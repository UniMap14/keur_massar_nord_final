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

from .permissions import a_role, est_maire, role_requis
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

    response = render(request, "foncier/geoportail.html", {
        "mes_parcelles_geojson": mes_parcelles_geojson,
    })
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ============================================================
# GÉOPORTAIL — VUE ADMIN (réservée aux agents)
# ============================================================

@login_required
@user_passes_test(_est_agent)
@role_requis("technique", "fiscal")
def carte_geoportail_admin(request):
    """
    Affiche le même géoportail à tous les agents autorisés, avec les
    informations et outils filtrés selon leur service.
    """
    context = {
        "active_section": "geoportail",
        "peut_technique": a_role(request.user, "technique"),
        "peut_fiscal": a_role(request.user, "fiscal"),
        "peut_modifier_cadastre": (
            a_role(request.user, "technique") and not est_maire(request.user)
        ),
    }
    response = render(request, "foncier/geoportail_admin.html", context)
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


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
CACHE_KEY_ADMIN = "geojson_parcelles_admin_fiscal_v4"
CACHE_KEY_ADMIN_CADASTRE = "geojson_parcelles_admin_cadastre_v4"
CACHE_KEY_ADMIN_FISCAL = "geojson_parcelles_admin_fiscal_view_v3"
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


def _proprietes_infrastructure_geojson(infra, peut_technique):
    details = infra.details or {}
    if not peut_technique:
        details = {key: value for key, value in details.items() if key != "Nombre d'employés"}

    proprietes = {
        "nom": infra.nom,
        "categorie": infra.categorie.label,
        "icone": infra.categorie.icone,
        "couleur": infra.categorie.couleur,
        "latitude": infra.latitude,
        "longitude": infra.longitude,
        "sous_type": infra.sous_type,
        "details": details,
    }
    if peut_technique:
        proprietes["id"] = infra.id
    return proprietes


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
    data_json = cache.get(CACHE_KEY_PUBLIC)
    if data_json is None:
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
        # On met en cache le JSON deja serialise (une chaine), pas le dict
        # Python : avec ~40000 features, (de)serialiser l'objet complet a
        # chaque lecture du cache coutait ~25s a elle seule, meme "a chaud".
        data_json = json.dumps(data)
        cache.set(CACHE_KEY_PUBLIC, data_json, None)  # pas d'expiration : invalidé par le signal

    return HttpResponse(data_json, content_type="application/json")


# ============================================================
# API GEOJSON PARCELLES — VERSION ADMIN
# Le Cadastre reçoit les données cadastrales, la Fiscalité les données
# fiscales et les infrastructures publiques, et le superviseur les deux.
# ============================================================

@login_required
@user_passes_test(_est_agent)
@role_requis("technique", "fiscal")
def api_parcelles_geojson_admin(request):
    """
    GeoJSON admin filtré selon le service : la Fiscalité reçoit les valeurs
    fiscales et les infrastructures, sans données nominatives cadastrales.
    """
    peut_technique = a_role(request.user, "technique")
    peut_fiscal = a_role(request.user, "fiscal")
    bbox_poly = _bbox_depuis_requete(request)
    if bbox_poly is None:
        return JsonResponse({"type": "FeatureCollection", "features": []})

    features = []

    qs = (
        Parcelle.objects
        .exclude(geom__isnull=True)
        .filter(geom__bboverlaps=bbox_poly)
        .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION)))
        .order_by("id")
    )
    if not peut_technique:
        qs = qs.filter(parcelle_active=True)
    qs = qs[:PARCELLES_MAX_PAR_REQUETE]
    if peut_technique:
        qs = qs.select_related("zone", "proprietaire").only(
            "id", "nicad", "superficie", "adresse_parcelle",
            "montant_taxe_annuelle", "valeur_locative", "statut_fiscal",
            "type_document", "reference_arrete", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier", "occupation_sol", "simulation_fiscale",
            "zone__nom", "proprietaire__nom", "proprietaire__prenom", "proprietaire__ni_cni",
        )
    else:
        qs = qs.only(
            "id", "montant_taxe_annuelle", "valeur_locative",
            "statut_fiscal", "simulation_fiscale",
        )

    infra_par_parcelle_admin = {}
    if not peut_technique:
        parcelle_ids = list(qs.values_list("id", flat=True))
        for infra in Infrastructure.objects.filter(parcelle_id__in=parcelle_ids).select_related("categorie"):
            infra_par_parcelle_admin.setdefault(infra.parcelle_id, []).append(
                _proprietes_infrastructure_geojson(infra, peut_technique)
            )

    for parcelle in qs.iterator():
        if not peut_technique:
            proprietes = {
                "id": parcelle.id,
                "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                "valeur_locative": float(parcelle.valeur_locative),
                "statut_fiscal": parcelle.statut_fiscal,
                "simulation_fiscale": parcelle.simulation_fiscale,
                "infrastructures": infra_par_parcelle_admin.get(parcelle.id, []),
            }
            features.append({
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": proprietes,
            })
            continue

        proprietes = {
            "id": parcelle.id,
            "nicad": parcelle.nicad,
            "num_lot": parcelle.nicad,
            "superficie": parcelle.superficie,
            "adresse_parcelle": parcelle.adresse_parcelle,
            "type_document": parcelle.type_document,
            "reference_arrete": parcelle.reference_arrete,
            "section_cadastrale": parcelle.section_cadastrale,
            "numero_parcelle": parcelle.numero_parcelle,
            "numero_lot": parcelle.numero_lot,
            "numero_titre_foncier": parcelle.numero_titre_foncier,
            "occupation_sol": parcelle.occupation_sol,
            "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
            "proprietaire": (
                f"{parcelle.proprietaire.prenom} {parcelle.proprietaire.nom}"
                if parcelle.proprietaire_id else None
            ),
            "proprietaire_nom": parcelle.proprietaire.nom if parcelle.proprietaire_id else None,
            "proprietaire_prenom": parcelle.proprietaire.prenom if parcelle.proprietaire_id else None,
            "proprietaire_cni": parcelle.proprietaire.ni_cni if parcelle.proprietaire_id else None,
        }
        if peut_fiscal:
            proprietes.update({
                "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                "valeur_locative": float(parcelle.valeur_locative),
                "statut_fiscal": parcelle.statut_fiscal,
                "simulation_fiscale": parcelle.simulation_fiscale,
            })
        features.append({
            "type": "Feature",
            "geometry": json.loads(parcelle.geojson_geom),
            "properties": proprietes,
        })

    return JsonResponse({"type": "FeatureCollection", "features": features})


@login_required
@user_passes_test(_est_agent)
@role_requis("technique", "fiscal")
def api_parcelles_toutes_geojson_admin(request):
    """GéoJSON admin : toutes les parcelles actives, avec les données
    autorisées au service concerné et les infrastructures publiques."""
    peut_technique = a_role(request.user, "technique")
    peut_fiscal = a_role(request.user, "fiscal")
    if peut_technique and peut_fiscal:
        cache_key = CACHE_KEY_ADMIN
    elif peut_technique:
        cache_key = CACHE_KEY_ADMIN_CADASTRE
    else:
        cache_key = CACHE_KEY_ADMIN_FISCAL
    data_json = cache.get(cache_key)
    if data_json is None:
        qs = (
            Parcelle.objects
            .exclude(geom__isnull=True)
            .filter(parcelle_active=True)
            .annotate(geojson_geom=AsGeoJSON(SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))
            .order_by("id")
        )
        if peut_technique:
            qs = qs.select_related("zone", "proprietaire").only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "montant_taxe_annuelle", "valeur_locative", "statut_fiscal",
                "type_document", "reference_arrete", "section_cadastrale", "numero_parcelle", "numero_lot", "numero_titre_foncier", "occupation_sol", "simulation_fiscale",
                "zone__nom", "proprietaire__nom", "proprietaire__prenom", "proprietaire__ni_cni",
            )
        else:
            qs = qs.only(
                "id", "montant_taxe_annuelle", "valeur_locative",
                "statut_fiscal", "simulation_fiscale",
            )

        infra_par_parcelle_admin = {}
        for infra in Infrastructure.objects.filter(parcelle_id__isnull=False).select_related("categorie"):
            infra_par_parcelle_admin.setdefault(infra.parcelle_id, []).append(
                _proprietes_infrastructure_geojson(infra, peut_technique)
            )

        features = []
        for parcelle in qs.iterator():
            if not peut_technique:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(parcelle.geojson_geom),
                    "properties": {
                        "id": parcelle.id,
                        "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                        "valeur_locative": float(parcelle.valeur_locative),
                        "statut_fiscal": parcelle.statut_fiscal,
                        "simulation_fiscale": parcelle.simulation_fiscale,
                        "infrastructures": infra_par_parcelle_admin.get(parcelle.id, []),
                    },
                })
                continue

            proprietes = {
                "id": parcelle.id,
                "nicad": parcelle.nicad,
                "num_lot": parcelle.nicad,
                "superficie": parcelle.superficie,
                "adresse_parcelle": parcelle.adresse_parcelle,
                "type_document": parcelle.type_document,
                "reference_arrete": parcelle.reference_arrete,
                "section_cadastrale": parcelle.section_cadastrale,
                "numero_parcelle": parcelle.numero_parcelle,
                "numero_lot": parcelle.numero_lot,
                "numero_titre_foncier": parcelle.numero_titre_foncier,
                "occupation_sol": parcelle.occupation_sol,
                "infrastructures": infra_par_parcelle_admin.get(parcelle.id, []),
                "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                "proprietaire": (
                    f"{parcelle.proprietaire.prenom} {parcelle.proprietaire.nom}"
                    if parcelle.proprietaire_id else None
                ),
                "proprietaire_nom": parcelle.proprietaire.nom if parcelle.proprietaire_id else None,
                "proprietaire_prenom": parcelle.proprietaire.prenom if parcelle.proprietaire_id else None,
                "proprietaire_cni": parcelle.proprietaire.ni_cni if parcelle.proprietaire_id else None,
            }
            if peut_fiscal:
                proprietes.update({
                    "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
                    "valeur_locative": float(parcelle.valeur_locative),
                    "statut_fiscal": parcelle.statut_fiscal,
                    "simulation_fiscale": parcelle.simulation_fiscale,
                })
            features.append({
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": proprietes,
            })
        infra_sans_parcelle_admin = [
            _proprietes_infrastructure_geojson(infra, peut_technique)
            for infra in Infrastructure.objects.filter(parcelle_id__isnull=True).select_related("categorie")
        ]

        data = {"type": "FeatureCollection", "features": features}
        if peut_technique:
            data["infrastructures_hors_parcelle"] = infra_sans_parcelle_admin
        data_json = json.dumps(data)
        cache.set(cache_key, data_json, None)

    return HttpResponse(data_json, content_type="application/json")


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
    if est_maire(request.user):
        return JsonResponse({
            "ok": False,
            "error": "Le maire peut consulter les parcelles, mais pas modifier leurs données."
        }, status=403)

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
        "numero_lot", "numero_titre_foncier", "proprietaire_nom",
        "proprietaire_prenom", "proprietaire_cni",
    }
    CHAMPS_FISCAUX = {
        "statut_fiscal", "montant_taxe_annuelle", "valeur_locative", "simulation_fiscale",
    }

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

    # Un propriétaire peut être créé ou complété directement depuis la fiche.
    champs_proprietaire = ("proprietaire_nom", "proprietaire_prenom", "proprietaire_cni")
    if any(champ in request.POST for champ in champs_proprietaire):
        nom = request.POST.get("proprietaire_nom", "").strip()
        prenom = request.POST.get("proprietaire_prenom", "").strip()
        cni = request.POST.get("proprietaire_cni", "").strip()
        if cni.upper() == "RETIRER":
            if nom or prenom:
                return JsonResponse({
                    "ok": False,
                    "error": "Laissez le nom et le prénom vides pour retirer le propriétaire."
                }, status=400)
            parcelle.proprietaire = None
            champs_modifies.append("proprietaire")
        elif nom or prenom or cni:
            if not (nom and prenom and cni):
                return JsonResponse({
                    "ok": False,
                    "error": "Renseignez le nom, le prénom et la CNI du propriétaire."
                }, status=400)
            if len(nom) > 100 or len(prenom) > 100 or len(cni) > 20:
                return JsonResponse({
                    "ok": False,
                    "error": "Le nom, le prénom ou la CNI dépasse la longueur autorisée."
                }, status=400)
            proprietaire = Propriétaire.objects.filter(ni_cni=cni).first()
            if proprietaire is None:
                proprietaire = Propriétaire.objects.create(
                    nom=nom,
                    prenom=prenom,
                    ni_cni=cni,
                )
            elif proprietaire.nom != nom or proprietaire.prenom != prenom:
                proprietaire.nom = nom
                proprietaire.prenom = prenom
                proprietaire.save(update_fields=["nom", "prenom"])
            parcelle.proprietaire = proprietaire
            champs_modifies.append("proprietaire")

    if champs_modifies:
        parcelle.save(update_fields=champs_modifies)

    resultat = {"ok": True, "id": parcelle.id}
    if a_role(request.user, "technique"):
        resultat.update({
            "nicad": parcelle.nicad,
            "superficie": parcelle.superficie,
            "adresse_parcelle": parcelle.adresse_parcelle,
            "type_document": parcelle.type_document,
            "occupation_sol": parcelle.occupation_sol,
            "reference_arrete": parcelle.reference_arrete,
            "section_cadastrale": parcelle.section_cadastrale,
            "numero_parcelle": parcelle.numero_parcelle,
            "numero_lot": parcelle.numero_lot,
            "numero_titre_foncier": parcelle.numero_titre_foncier,
            "proprietaire": (
                f"{parcelle.proprietaire.prenom} {parcelle.proprietaire.nom}"
                if parcelle.proprietaire_id else None
            ),
            "proprietaire_nom": parcelle.proprietaire.nom if parcelle.proprietaire_id else None,
            "proprietaire_prenom": parcelle.proprietaire.prenom if parcelle.proprietaire_id else None,
            "proprietaire_cni": parcelle.proprietaire.ni_cni if parcelle.proprietaire_id else None,
        })
    if a_role(request.user, "fiscal"):
        resultat.update({
            "statut_fiscal": parcelle.statut_fiscal,
            "montant_taxe_annuelle": float(parcelle.montant_taxe_annuelle),
            "valeur_locative": float(parcelle.valeur_locative),
            "simulation_fiscale": parcelle.simulation_fiscale,
        })
    return JsonResponse(resultat)


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


def _arrondi(valeur):
    return int(valeur.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@require_POST
def simuler_fiscalite(request):
    form = SimulateurFiscalForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    data = form.cleaned_data
    type_sim = data["type_simulation"]
    revenu = data["revenu"]

    resultat = {"ok": True, "type": type_sim}

    if type_sim == "cfpb":
        secteur_cfpb = data["cfpb_secteur"]
        est_usine = secteur_cfpb == "usine"
        taux = Decimal("0.075") if est_usine else Decimal("0.05")
        valeur_locative = revenu
        residence_principale = bool(data.get("cfpb_residence_principale"))
        abattement = Decimal("500000") if (residence_principale and not est_usine) else Decimal("0")
        abattement = min(abattement, valeur_locative)
        base_imposable = valeur_locative - abattement
        cfpb = base_imposable * taux
        libelle_bien = "usine / établissement industriel" if est_usine else "immeuble standard"

        detail_cfpb = []
        if abattement > 0:
            detail_cfpb.append({"tranche": "Abattement résidence principale", "taux": 0, "montant": -_arrondi(abattement)})
        detail_cfpb.append({"tranche": f"Base imposable x {float(taux) * 100:.1f} %", "taux": float(taux) * 100, "montant": _arrondi(cfpb)})

        resultat.update({
            "valeur_locative": _arrondi(valeur_locative),
            "abattement": _arrondi(abattement),
            "base_imposable": _arrondi(base_imposable),
            "taux_applique": float(taux) * 100,
            "impot": _arrondi(cfpb),
            "detail_tranches": detail_cfpb,
            "reference": f"Contribution Foncière des Propriétés Bâties (CFPB) = "
                         f"{float(taux) * 100:.1f} % de la valeur locative ({libelle_bien}), "
                         f"abattement de 500 000 FCFA si résidence principale du propriétaire "
                         f"(Art. 329-334 CGI). Constructions neuves exonérées jusqu'à la 6e année.",
        })

    elif type_sim == "cfpnb":
        est_terrain_nu = data["cfpnb_nature"] == "terrain_nu"
        taux = Decimal("0.07") if est_terrain_nu else Decimal("0.05")
        valeur_venale = revenu
        impot = valeur_venale * taux
        nature_terrain = "terrain nu" if est_terrain_nu else "zone de culture"
        libelle_taux = "5 % + surtaxe de 2 %" if est_terrain_nu else "5 %"

        resultat.update({
            "valeur_venale": _arrondi(valeur_venale),
            "taux_applique": float(taux * 100),
            "impot": _arrondi(impot),
            "detail_tranches": [{
                "tranche": f"Valeur vénale x {libelle_taux}",
                "taux": float(taux * 100),
                "montant": _arrondi(impot),
            }],
            "reference": f"Estimation CFPNB sur la valeur vénale déclarée ({nature_terrain}), "
                         f"selon la formule de simulation foncière déjà utilisée dans le projet : "
                         f"{libelle_taux}.",
        })

    elif type_sim in ("irf", "teom"):
        taux = data["taux_irf"] if type_sim == "irf" else data["taux_teom"]
        impot = revenu * taux / Decimal("100")
        is_irf = type_sim == "irf"
        libelle = "IRF" if is_irf else "TEOM"
        base_label = "Revenu foncier annuel déclaré" if is_irf else "Valeur locative annuelle déclarée"

        resultat.update({
            "base_imposable": _arrondi(revenu),
            "taux_applique": float(taux),
            "impot": _arrondi(impot),
            "detail_tranches": [{
                "tranche": f"Base déclarée x {taux} %",
                "taux": float(taux),
                "montant": _arrondi(impot),
            }],
            "libelle_base": base_label,
            "reference": f"Estimation {libelle} calculée avec le taux saisi par l'utilisateur. "
                         "Ce taux doit être confirmé auprès de l'administration fiscale locale.",
        })

    else:
        return JsonResponse({"ok": False, "errors": "Type d'imposition inconnu."}, status=400)

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
    cache.delete(CACHE_KEY_ADMIN_CADASTRE)
    cache.delete(CACHE_KEY_ADMIN_FISCAL)


@receiver([post_save, post_delete], sender=Taxation)
def _invalider_cache_parcelles_fiscales(sender, **kwargs):
    cache.delete(CACHE_KEY_ADMIN_FISCAL)


@receiver([post_save, post_delete], sender=Infrastructure)
@receiver([post_save, post_delete], sender=CategorieInfrastructure)
def _invalider_cache_infrastructures(sender, **kwargs):
    cache.delete(CACHE_KEY_PUBLIC)
    cache.delete(CACHE_KEY_ADMIN)
    cache.delete(CACHE_KEY_ADMIN_CADASTRE)
    cache.delete(CACHE_KEY_ADMIN_FISCAL)


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
    rayon_m = max(140.0, 0.9 * max(largeur_m, hauteur_m))
    rayon_m = min(rayon_m, 500.0)
    tampon_deg = rayon_m / 111320.0

    try:
        from django.contrib.gis.db.models.functions import Distance as _DistanceVoisines
        from django.contrib.gis.geos import Polygon as _PolygonVoisines
        _xmin, _ymin, _xmax, _ymax = parcelle.geom.extent
        zone_recherche = _PolygonVoisines.from_bbox((
            _xmin - tampon_deg, _ymin - tampon_deg,
            _xmax + tampon_deg, _ymax + tampon_deg,
        ))
        zone_recherche.srid = parcelle.geom.srid
        voisines = list(
            Parcelle.objects.filter(geom__intersects=zone_recherche)
            .exclude(pk=parcelle.pk)
            .annotate(_distance_voisine=_DistanceVoisines("geom", parcelle.geom))
            .order_by("_distance_voisine")
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


def _format_superficie_are_ca(superficie_m2):
    """Formate une superficie en m2 au format cadastral senegalais
    "Xa YYca" (1 are = 100 m2, 1 centiare = 1 m2), ex: 162 m2 -> "1a 62ca"."""
    if not superficie_m2:
        return "-"
    total_ca = int(round(float(superficie_m2)))
    ares = total_ca // 100
    centiares = total_ca % 100
    return "{}a {:02d}ca".format(ares, centiares)


def _generer_image_plan_type_officiel(parcelle, voisines, taille_px_cible=1700):
    """Dessine le plan de situation sur le modele d'un extrait de plan
    cadastral officiel : parcelles voisines en trait fin avec leur
    numero, parcelle principale en rouge avec cotes (longueur de chaque
    cote) et reperes B1..Bn a chaque sommet, fleche du Nord -- sans
    grille de coordonnees (absente du modele officiel). Le cadre du
    dessin epouse la vraie forme (largeur/hauteur) du nuage de
    parcelles trouvees, sans etre force a un carre, pour ne jamais
    laisser de grandes zones blanches inutiles. Renvoie
    (buffer_png, texte_echelle, largeur_px, hauteur_px)."""
    import io as io_module
    import math
    from PIL import Image, ImageDraw, ImageFont

    sommets_principal = _sommets_parcelle_utm(parcelle)

    polygones_voisins = []
    for voisine in voisines:
        try:
            pts = _anneau_exterieur_utm(voisine.geom[0])
        except Exception:
            continue
        if pts:
            polygones_voisins.append((voisine, pts))

    tous_points = list(sommets_principal)
    for _, pts in polygones_voisins:
        tous_points.extend(pts)

    xs = [p[0] for p in tous_points]
    ys = [p[1] for p in tous_points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    # Emprise reelle des donnees : chaque axe garde sa propre etendue
    # (pas de carre impose), avec une marge de securite minime -- le
    # cadre du dessin epouse ainsi la vraie forme du nuage de parcelles.
    etendue_brute_x = max(xmax - xmin, 10.0)
    etendue_brute_y = max(ymax - ymin, 10.0)
    marge_m_x = etendue_brute_x * 0.025 + 1
    marge_m_y = etendue_brute_y * 0.025 + 1
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2
    etendue_x = etendue_brute_x + 2 * marge_m_x
    etendue_y = etendue_brute_y + 2 * marge_m_y
    xmin, xmax = cx - etendue_x / 2, cx + etendue_x / 2
    ymin, ymax = cy - etendue_y / 2, cy + etendue_y / 2

    echelle_px_par_m = taille_px_cible / max(etendue_x, etendue_y)
    taille_px_x = max(220, int(etendue_x * echelle_px_par_m))
    taille_px_y = max(220, int(etendue_y * echelle_px_par_m))

    def vers_px(point_x, point_y):
        px = (point_x - xmin) * echelle_px_par_m
        py = taille_px_y - (point_y - ymin) * echelle_px_par_m
        return (px, py)

    img = Image.new("RGB", (taille_px_x, taille_px_y), "white")
    draw = ImageDraw.Draw(img)

    try:
        police_num = ImageFont.load_default(size=26)
        police_label = ImageFont.load_default(size=20)
        police_cote = ImageFont.load_default(size=18)
        police_nord = ImageFont.load_default(size=24)
    except TypeError:
        police_num = police_label = police_cote = police_nord = ImageFont.load_default()

    # Parcelles voisines : trait fin noir + numero au centre, avec une
    # taille de police adaptee a la taille reelle de chaque parcelle a
    # l'ecran (pour ne jamais deborder), et pas de numero du tout si la
    # parcelle est trop petite pour l'accueillir proprement.
    cache_polices = {}

    def _police_adaptee(taille_cible):
        taille_cible = max(6, min(26, int(taille_cible)))
        if taille_cible not in cache_polices:
            try:
                cache_polices[taille_cible] = ImageFont.load_default(size=taille_cible)
            except TypeError:
                cache_polices[taille_cible] = ImageFont.load_default()
        return cache_polices[taille_cible]

    def _ajuster_texte_dans_boite(texte, largeur_max, hauteur_max, taille_min=7, taille_max=26):
        """Cherche la plus grande taille de police (mesuree reellement,
        pas estimee) qui fait tenir `texte` dans une boite de
        largeur_max x hauteur_max px, avec une petite marge de securite.
        Renvoie None si meme la plus petite taille deborde encore."""
        largeur_cible = largeur_max * 0.86
        hauteur_cible = hauteur_max * 0.86
        for taille in range(taille_max, taille_min - 1, -1):
            police = _police_adaptee(taille)
            boite = draw.textbbox((0, 0), texte, font=police)
            larg = boite[2] - boite[0]
            haut = boite[3] - boite[1]
            if larg <= largeur_cible and haut <= hauteur_cible:
                return police
        return None

    for voisine, pts in polygones_voisins:
        pts_px = [vers_px(px, py) for px, py in pts]
        if len(pts_px) >= 2:
            draw.polygon(pts_px, outline=(40, 40, 40), width=2)
            xs_v = [p[0] for p in pts_px]
            ys_v = [p[1] for p in pts_px]
            largeur_bbox = max(xs_v) - min(xs_v)
            hauteur_bbox = max(ys_v) - min(ys_v)
            centre_x = sum(xs_v) / len(pts_px)
            centre_y = sum(ys_v) / len(pts_px)
            etiquette = voisine.numero_parcelle or (voisine.nicad[-4:] if voisine.nicad else "?")
            police_voisine = _ajuster_texte_dans_boite(str(etiquette), largeur_bbox, hauteur_bbox)
            if police_voisine is not None:
                draw.text(
                    (centre_x, centre_y), str(etiquette), fill=(30, 30, 30),
                    font=police_voisine, anchor="mm",
                )

    # Parcelle principale : contour rouge epais, cotes et reperes B1..Bn.
    pts_px = [vers_px(px, py) for px, py in sommets_principal]
    if len(pts_px) >= 2:
        draw.polygon(pts_px, outline=(192, 20, 20), width=6)

        centre_x = sum(p[0] for p in pts_px) / len(pts_px)
        centre_y = sum(p[1] for p in pts_px) / len(pts_px)

        n = len(pts_px)
        for i in range(n):
            x1, y1 = pts_px[i]
            x2, y2 = pts_px[(i + 1) % n]

            ux1, uy1 = sommets_principal[i]
            ux2, uy2 = sommets_principal[(i + 1) % n]
            longueur = math.hypot(ux2 - ux1, uy2 - uy1)

            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            norm = math.hypot(dx, dy) or 1
            nvx, nvy = -dy / norm, dx / norm
            vers_centre_x, vers_centre_y = centre_x - mx, centre_y - my
            if nvx * vers_centre_x + nvy * vers_centre_y > 0:
                nvx, nvy = -nvx, -nvy
            decalage = 26
            draw.text(
                (mx + nvx * decalage, my + nvy * decalage),
                "{:.2f}".format(longueur),
                fill=(140, 10, 10), font=police_cote, anchor="mm",
            )

            draw.ellipse([x1 - 4, y1 - 4, x1 + 4, y1 + 4], fill=(192, 20, 20))
            bx, by = x1 + nvx * 18 - (dx / norm) * 18, y1 + nvy * 18 - (dy / norm) * 18
            draw.text((bx, by), "B{}".format(i + 1), fill=(192, 20, 20), font=police_label, anchor="mm")

        xs_p = [p[0] for p in pts_px]
        ys_p = [p[1] for p in pts_px]
        etiquette_principale = parcelle.numero_parcelle or (parcelle.nicad[-4:] if parcelle.nicad else "?")
        police_principale = _ajuster_texte_dans_boite(
            str(etiquette_principale), max(xs_p) - min(xs_p), max(ys_p) - min(ys_p),
            taille_min=8, taille_max=28,
        ) or _police_adaptee(8)
        draw.text(
            (centre_x, centre_y), str(etiquette_principale), fill=(150, 15, 15),
            font=police_principale, anchor="mm",
        )

    # Fleche du Nord (coin haut droit).
    nx0 = taille_px_x - 70
    ny0 = 90
    draw.line([(nx0, ny0 + 46), (nx0, ny0 - 26)], fill=(20, 20, 20), width=4)
    draw.polygon([(nx0, ny0 - 42), (nx0 - 13, ny0 - 16), (nx0 + 13, ny0 - 16)], fill=(20, 20, 20))
    draw.text((nx0, ny0 - 56), "N", fill=(20, 20, 20), font=police_nord, anchor="mm")

    tampon = io_module.BytesIO()
    img.save(tampon, format="PNG")
    tampon.seek(0)

    denominateurs_usuels = [100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 20000]
    denominateur_brut = (max(etendue_x, etendue_y) * 1000) / 180
    echelle_texte = "1 / {}e".format(next(
        (d for d in denominateurs_usuels if d >= denominateur_brut), denominateurs_usuels[-1]
    ))

    return tampon, echelle_texte, taille_px_x, taille_px_y


@login_required
def extrait_cadastral_pdf_view(request, pk):
    """
    Genere l'extrait de plan foncier (PLAN POUR AUTORISATION DE CONSTRUIRE)
    en PDF, calque sur le modele exact d'un extrait de plan cadastral
    officiel delivre par le Bureau du Cadastre : en-tete administratif
    complet (Republique du Senegal, Ministere, DGID, Centre des Services
    Fiscaux, Bureau du Cadastre), encadre Region/Departement/Commune,
    cartouche NICAD/titre/lot/superficie, plan de situation avec cotes
    et reperes B1..Bn, et bande de certification en bas de page.
    """
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
    from django.utils import timezone
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

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4
    marge = 16 * mm
    NOIR = HexColor("#111111")
    GRIS = HexColor("#444444")

    y = hauteur - 14 * mm

    # ----- En-tete administratif, sur le modele du document officiel -----
    c.setFillColor(NOIR)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(marge, y, "REPUBLIQUE DU SENEGAL")
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawString(marge, y - 4 * mm, "Un Peuple - Un But - Une Foi")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(marge, y - 9 * mm, "MINISTERE DE L'ECONOMIE, DES FINANCES ET DU PLAN")
    # Le logo contient deja le texte "Direction Generale des Impots et
    # des Domaines" -- pas besoin de le redessiner a cote.
    taille_logo = 11 * mm
    x_logo = marge
    y_logo_haut = y - 10.5 * mm
    try:
        from django.contrib.staticfiles import finders
        chemin_logo = finders.find("foncier/img/logo-dgid.png")
        if chemin_logo:
            logo_img = ImageReader(chemin_logo)
            largeur_logo_native, hauteur_logo_native = logo_img.getSize()
            largeur_logo = taille_logo * (largeur_logo_native / hauteur_logo_native)
            c.drawImage(
                logo_img, x_logo, y_logo_haut - taille_logo,
                width=largeur_logo, height=taille_logo,
                preserveAspectRatio=True, mask="auto",
            )
    except Exception:
        pass
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 7)
    c.drawString(marge, y - 24 * mm, "Centre des Services Fiscaux de Keur Massar")
    c.drawString(marge, y - 28 * mm, "Bureau du Cadastre")

    largeur_boite = 55 * mm
    hauteur_boite = 20 * mm
    x_boite = largeur - marge - largeur_boite
    y_boite = y + 2 * mm
    c.setStrokeColor(NOIR)
    c.setLineWidth(0.6)
    c.rect(x_boite, y_boite - hauteur_boite, largeur_boite, hauteur_boite, fill=False, stroke=True)
    lignes_boite = [
        ("Region", "Dakar"),
        ("Departement", "Keur Massar"),
        ("Commune", "Keur Massar Nord"),
    ]
    yc = y_boite - 5 * mm
    c.setFont("Helvetica", 7.5)
    for label, valeur in lignes_boite:
        c.setFillColor(GRIS)
        c.drawString(x_boite + 2 * mm, yc, "{} :".format(label))
        c.setFillColor(NOIR)
        c.drawString(x_boite + 22 * mm, yc, valeur)
        yc -= 5.5 * mm

    y -= 34 * mm

    c.setStrokeColor(NOIR)
    c.setLineWidth(1.2)
    cx_nord = largeur / 2
    c.line(cx_nord, y, cx_nord, y - 5 * mm)
    c.line(cx_nord, y, cx_nord - 1.8 * mm, y - 2.2 * mm)
    c.line(cx_nord, y, cx_nord + 1.8 * mm, y - 2.2 * mm)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(NOIR)
    c.drawCentredString(cx_nord, y + 1.5 * mm, "N")
    y -= 9 * mm

    titre_foncier = parcelle.numero_titre_foncier or "-"
    parcelle_label = parcelle.numero_parcelle or parcelle.nicad
    zone_label = parcelle.zone.nom if parcelle.zone_id else ""
    reference_arrete = (getattr(parcelle, "reference_arrete", "") or "").strip()

    TITRES_PAR_MOTIF = {
        "Extrait de plan — Autorisation de construire": "PLAN POUR AUTORISATION DE CONSTRUIRE",
        "Extrait de plan — Demande de régularisation": "PLAN POUR REGULARISATION",
        "Extrait de plan — Situation": "PLAN DE SITUATION",
        "Extrait de plan — Délimitation": "PLAN DE DELIMITATION",
        "Extrait de plan — Autres": "EXTRAIT DE PLAN",
    }
    motif_libelle = demande.type_demande.libelle if demande.type_demande_id else ""
    est_regularisation = motif_libelle == "Extrait de plan — Demande de régularisation"
    titre_document_plan = TITRES_PAR_MOTIF.get(motif_libelle, "EXTRAIT DE PLAN FONCIER")

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(largeur / 2, y, titre_document_plan)
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    if parcelle.numero_titre_foncier:
        c.drawCentredString(largeur / 2, y, "Mt du Titre Foncier {}/DP".format(titre_foncier))
        y -= 5 * mm
    libelle_lot = "Lot n° {}".format(parcelle_label)
    if est_regularisation and reference_arrete:
        libelle_lot += " (Arrêté n° {})".format(reference_arrete)
    elif zone_label:
        libelle_lot += " ({})".format(zone_label)
    c.drawCentredString(largeur / 2, y, libelle_lot)
    y -= 5 * mm
    c.drawCentredString(largeur / 2, y, "Superficie = {}".format(_format_superficie_are_ca(parcelle.superficie)))
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(largeur / 2, y, "NICAD : {}".format(parcelle.nicad))
    y -= 8 * mm

    c.setStrokeColor(GRIS)
    c.setLineWidth(0.4)
    c.line(marge, y, largeur - marge, y)
    y -= 6 * mm

    dispo_largeur = largeur - 2 * marge
    dispo_hauteur = max(70 * mm, y - 47 * mm)
    echelle_texte = "-"
    hauteur_plan_reelle = dispo_hauteur
    try:
        voisines = _voisines_parcelle(parcelle, max_resultats=110)
        image_plan, echelle_texte, largeur_px, hauteur_px = _generer_image_plan_type_officiel(parcelle, voisines)
        ratio_image = hauteur_px / largeur_px
        if dispo_largeur * ratio_image <= dispo_hauteur:
            largeur_plan_reelle = dispo_largeur
            hauteur_plan_reelle = dispo_largeur * ratio_image
        else:
            hauteur_plan_reelle = dispo_hauteur
            largeur_plan_reelle = dispo_hauteur / ratio_image
        x_plan = marge + (dispo_largeur - largeur_plan_reelle) / 2
        c.drawImage(
            ImageReader(image_plan), x_plan, y - hauteur_plan_reelle,
            width=largeur_plan_reelle, height=hauteur_plan_reelle,
            preserveAspectRatio=True, mask="auto",
        )
    except Exception:
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(largeur / 2, y - dispo_hauteur / 2, "Plan non disponible pour cette parcelle.")

    y -= hauteur_plan_reelle + 8 * mm

    c.setFont("Helvetica", 8.5)
    c.setFillColor(NOIR)
    c.drawString(marge, y, "A Keur Massar Nord, le {}".format(timezone.now().strftime("%d/%m/%Y")))
    y -= 5 * mm
    c.drawString(marge, y, "Numéro : {}/{}".format(numero_doc, timezone.now().strftime("%d-%m-%Y")))

    c.setFont("Helvetica", 8.5)
    c.drawRightString(largeur - marge, y + 5 * mm, "Echelle = {}".format(echelle_texte))

    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(largeur - marge, y, "Le Chef du Bureau du Cadastre")
    y -= 14 * mm
    c.setStrokeColor(GRIS)
    c.setLineWidth(0.4)
    c.line(largeur - marge - 55 * mm, y, largeur - marge, y)
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(GRIS)
    c.drawRightString(largeur - marge, y - 4 * mm, "Cachet et signature")

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NOIR)
    c.drawCentredString(largeur / 2, y, "Ce plan ne constitue pas un titre de propriété")

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
