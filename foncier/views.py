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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import json
from decimal import Decimal, ROUND_HALF_UP

from .models import Signalement
from .forms import SignalementForm

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .forms import SimulateurFiscalForm


from .forms import ContactForm
from .forms import ContribuableForm, PaiementForm
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
)
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Prefetch


def _est_agent(user):
    return user.is_staff


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

    context = {
        "total_parcelles": total_parcelles,
        "total_proprietaires": total_proprietaires,
        "total_taxes": total_taxes,
        "parcelles_en_retard": parcelles_en_retard,
        "top_retardaires": top_retardaires,
        "quartiers": quartiers,

        # --- panneau "en chiffres" du hero ---
        # Chiffres démographiques/administratifs saisis manuellement pour
        # le moment (données non issues de la base). À remplacer par des
        # requêtes réelles quand les données correspondantes seront prêtes.
        'population': "380 000",
        'superficie': "15,4",
        'nb_quartiers': 104,
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
    """Affiche la page publique du géoportail (aucune donnée fiscale)."""
    return render(request, "foncier/geoportail.html")


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
TOLERANCE_SIMPLIFICATION_TOUTES = 0.0003  # bien plus grossier : vue de toute la commune dézoomée

CACHE_KEY_PUBLIC = "geojson_parcelles_public"
CACHE_KEY_ADMIN = "geojson_parcelles_admin"
CACHE_TTL_SECONDES = 120  # invalidé de toute façon dès qu'une parcelle est modifiée

# La commune compte ~38 000 parcelles : les envoyer TOUTES au navigateur en un
# seul GeoJSON (comme le faisait ce fichier avant) fait planter/bloquer la
# carte (requête PostGIS trop lourde + Leaflet incapable d'afficher 38 000
# polygones d'un coup). On limite donc désormais chaque réponse à la zone
# visible de la carte (bbox) ET à un plafond de sécurité, même si la zone
# demandée contient encore trop de parcelles.
PARCELLES_MAX_PAR_REQUETE = 1500


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
        .annotate(geojson_geom=AsGeoJSON(Simplify("geom", TOLERANCE_SIMPLIFICATION)))
        .only(
            "id", "nicad", "superficie", "adresse_parcelle",
            "occupation_sol", "zone__nom",
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
            .select_related("zone")
            .annotate(geojson_geom=AsGeoJSON(Simplify("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))
            .only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "occupation_sol", "zone__nom",
            )
            .order_by("id")
        )

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(parcelle.geojson_geom),
                "properties": {
                    "nicad": parcelle.nicad,
                    "num_lot": parcelle.nicad,
                    "superficie": parcelle.superficie,
                    "adresse_parcelle": parcelle.adresse_parcelle,
                    "occupation_sol": parcelle.occupation_sol,
                    "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                },
            }
            for parcelle in qs.iterator()
        ]
        data = {"type": "FeatureCollection", "features": features}
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
        .annotate(geojson_geom=AsGeoJSON(Simplify("geom", TOLERANCE_SIMPLIFICATION)))
        .only(
            "id", "nicad", "superficie", "adresse_parcelle",
            "montant_taxe_annuelle", "valeur_locative", "statut_fiscal",
            "type_document", "reference_arrete", "occupation_sol",
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
                "occupation_sol": parcelle.occupation_sol,
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
            .select_related("zone", "proprietaire")
            .annotate(geojson_geom=AsGeoJSON(Simplify("geom", TOLERANCE_SIMPLIFICATION_TOUTES)))
            .only(
                "id", "nicad", "superficie", "adresse_parcelle",
                "montant_taxe_annuelle", "valeur_locative", "statut_fiscal",
                "type_document", "reference_arrete", "occupation_sol",
                "zone__nom", "proprietaire__nom", "proprietaire__prenom",
            )
            .order_by("id")
        )

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
                    "occupation_sol": parcelle.occupation_sol,
                    "zone_nom": parcelle.zone.nom if parcelle.zone_id else None,
                    "proprietaire": (
                        f"{parcelle.proprietaire.prenom} {parcelle.proprietaire.nom}"
                        if parcelle.proprietaire_id else None
                    ),
                },
            }
            for parcelle in qs.iterator()
        ]
        data = {"type": "FeatureCollection", "features": features}
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
        "reference_arrete": parcelle.reference_arrete,
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
    Version temporaire : affiche les quartiers depuis la table
    'kmsn_quartier' (nom du quartier via QRT_VLG_HA), si elle a été
    importée. Si elle n'existe pas encore (aucun shapefile de quartiers
    importé), on renvoie simplement une liste vide plutôt que de faire
    planter la carte : les parcelles doivent pouvoir s'afficher même
    sans ce calque de zones.
    """
    from django.db.utils import ProgrammingError

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    "QRT_VLG_HA" AS nom,
                    ST_AsGeoJSON(ST_Transform(geom, 4326)) AS geometry
                FROM kmsn_quartier
            """)
            rows = cursor.fetchall()
    except ProgrammingError:
        # Table absente : pas encore de shapefile de quartiers importé.
        connection.rollback()
        rows = []

    features = [
        {
            "type": "Feature",
            "geometry": json.loads(geometry),
            "properties": {
                "nom": nom,
            },
        }
        for nom, geometry in rows
    ]

    return JsonResponse({"type": "FeatureCollection", "features": features})


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


def infrastructures(request):
    """
    Page publique des infrastructures : chiffres clés par catégorie,
    détail par catégorie (liste réelle des équipements), avec une
    recherche/filtre facultatif par nom, quartier ou catégorie.
    """

    q = request.GET.get('q', '').strip()
    categorie_code = request.GET.get('categorie', '').strip()

    infra_qs = Infrastructure.objects.all().order_by('nom')

    if q:
        infra_qs = infra_qs.filter(
            Q(nom__icontains=q) | Q(quartier__icontains=q)
        )

    if categorie_code:
        infra_qs = infra_qs.filter(categorie__code=categorie_code)

    categories = (
        CategorieInfrastructure.objects
        .annotate(total_infra=Count('infrastructures', distinct=True))
        .prefetch_related(
            Prefetch('infrastructures', queryset=infra_qs, to_attr='infrastructures_filtrees')
        )
        .order_by('ordre', 'label')
    )

    # Pour la grille "chiffres clés" en haut de page : on garde le total
    # RÉEL par catégorie (pas filtré par la recherche), pour ne pas fausser
    # les statistiques globales même quand l'utilisateur filtre la liste.
    chiffres_cles = (
        CategorieInfrastructure.objects
        .annotate(total=Count('infrastructures', distinct=True))
        .order_by('ordre', 'label')
    )

    # Liste des catégories pour le menu déroulant du filtre
    toutes_categories = CategorieInfrastructure.objects.order_by('ordre', 'label')

    context = {
        'infrastructures': chiffres_cles,   # utilisé par la grille de chiffres clés
        'categories': categories,           # utilisé par les panneaux détaillés
        'toutes_categories': toutes_categories,
        'q': q,
        'categorie_code': categorie_code,
    }
    return render(request, 'foncier/infrastructures.html', context)


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
                    subject=f"[KMS Nord] Nouveau signalement : {objet.titre}",
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
    context = {
        'population': "380 000",        # ANSD, SES Dakar 2024 ; RGPH-2023 donnait 224 765 hab.
        'annee_population': 2024,
        'superficie': "15,4",
        'nb_quartiers': 104,
        'annee_creation': 2021,
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

        # Répartition par occupation du sol (les 6 catégories les plus
        # fréquentes, pour ne pas afficher une liste trop longue).
        repartition = (
            Parcelle.objects
            .exclude(occupation_sol='')
            .values('occupation_sol')
            .annotate(total=Count('id'))
            .order_by('-total')[:6]
        )
        max_total = repartition[0]['total'] if repartition else 1
        context['repartition_occupation'] = [
            {
                'label': r['occupation_sol'],
                'total': r['total'],
                'pourcentage': round(100 * r['total'] / nb_parcelles, 1),
                'largeur_barre': round(100 * r['total'] / max_total, 1),
            }
            for r in repartition
        ]

    # --- Infrastructures publiques réellement recensées ---
    context['nb_infrastructures'] = Infrastructure.objects.count()
    context['repartition_infrastructures'] = (
        CategorieInfrastructure.objects
        .annotate(total=Count('infrastructures'))
        .filter(total__gt=0)
        .order_by('-total')
    )

    return render(request, 'foncier/statistiques.html', context)


# ============================================================
# WEBHOOKS PAIEMENT EN LIGNE (appelés par les serveurs Orange/Wave,
# jamais par un navigateur : pas de session, pas de jeton CSRF)
#
# ⚠️ Les deux vues ci-dessous n'ont pas pu être testées contre de vrais
# appels Orange Money / Wave (aucun compte marchand disponible ici).
# La vérification de signature/authenticité du webhook — INDISPENSABLE
# en production pour empêcher quiconque de "confirmer" un faux paiement
# en appelant cette URL directement — doit être ajoutée en suivant la
# documentation officielle de chaque opérateur avant la mise en ligne.
# ============================================================

@csrf_exempt
@require_POST
def paiement_webhook_orange(request):
    return _traiter_webhook_paiement(request, "OM-")


@csrf_exempt
@require_POST
def paiement_webhook_wave(request):
    return _traiter_webhook_paiement(request, "WAVE-")


def _traiter_webhook_paiement(request, prefixe_attendu):
    try:
        donnees = json.loads(request.body.decode() or "{}")
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    # TODO : vérifier ici la signature/authenticité du webhook selon la
    # documentation de l'opérateur avant de faire confiance à "donnees".

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
    c.drawString(marge, hauteur - 16 * mm, "KMS Nord")
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
    c.drawString(marge, 13 * mm, f"Édité le {paiement.date_paiement.today().strftime('%d/%m/%Y')} depuis l'espace citoyen KMS Nord.")

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