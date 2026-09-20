from django.contrib.gis import admin
from .models import GuideFiscal
from django.db.models import Sum
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline  # Style moderne de Django Unfold
from unfold.sites import UnfoldAdminSite
from .models import Signalement

from .models import (
    Zone,
    Propriétaire,
    Parcelle,
    Contribuable,
    TypeTaxe,
    Taxation,
    Paiement,
    ProfilCitoyen,
    MessageContact,
    CategorieInfrastructure,
    Infrastructure,
    Actualite,
)


def fcfa(valeur):
    """Formatage FCFA cohérent (style français, espace comme séparateur de
    milliers) utilisé partout dans ce fichier, y compris pour les valeurs
    manquantes (None) qui ne doivent jamais faire planter l'admin."""
    if valeur is None:
        return "—"
    try:
        return f"{valeur:,.0f} FCFA".replace(",", " ")
    except (TypeError, ValueError):
        return "—"


# ==============================================================================
# 1. CRÉATION DU SITE D'ADMINISTRATION AVEC TABLEAU DE BORD (DASHBOARD)
# ==============================================================================
class FoncierAdminSite(UnfoldAdminSite):
    # NOTE : ces trois valeurs doivent rester identiques à SITE_HEADER /
    # SITE_TITLE dans le dict UNFOLD de settings.py — les deux mécanismes
    # coexistent, on les garde synchronisés plutôt que de parier sur lequel
    # des deux l'emporte.
    site_header = "KEUR MASSAR NORD — Foncier & Fiscal"
    site_title = "KEUR MASSAR NORD Admin"
    index_title = "Tableau de Bord Analytique"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Calculs financiers et statistiques en temps réel
        total_recouvre = Paiement.objects.aggregate(Sum('montant'))['montant__sum'] or 0
        total_du = Taxation.objects.aggregate(Sum('montant_du'))['montant_du__sum'] or 0
        # Clé réelle du choix (voir Parcelle.STATUTS_FISCAUX) : "EN_RETARD",
        # pas "En retard" — l'ancien filtre ne trouvait jamais aucune ligne.
        parcelles_en_retard = Parcelle.objects.filter(statut_fiscal="EN_RETARD").count()
        total_proprios = Propriétaire.objects.count()

        # Injection des KPI Cards dans le template Django Unfold
        extra_context.update({
            "kpis": [
                {
                    "title": "Recouvrement Total",
                    "value": fcfa(total_recouvre),
                    "description": "Total des taxes collectées",
                    "icon": "payments",
                    "color": "green",
                },
                {
                    "title": "Restes à Recouvrer (Dû)",
                    "value": fcfa(total_du - total_recouvre),
                    "description": "Montant restant à percevoir",
                    "icon": "money_off",
                    "color": "red",
                },
                {
                    "title": "Contentieux Fonciers",
                    "value": parcelles_en_retard,
                    "description": "Parcelles avec statut 'En retard'",
                    "icon": "gavel",
                    "color": "orange",
                },
                {
                    "title": "Propriétaires Enregistrés",
                    "value": total_proprios,
                    "description": "Citoyens dans la base SIG",
                    "icon": "people",
                    "color": "blue",
                },
            ]
        })
        return super().index(request, extra_context)


# On personnalise l'instance d'admin EXISTANTE au lieu d'en créer une nouvelle.
# Créer une nouvelle instance (admin.site = FoncierAdminSite()) casse la
# cohérence entre django.contrib.admin.site et django.contrib.gis.admin.site
# (deux objets distincts) et provoque une RecursionError au démarrage.
admin.site.__class__ = FoncierAdminSite


# ==============================================================================
# 2. ENREGISTREMENT ET CONFIGURATION DES MODÈLES SUR LE NOUVEL ADMIN
# ==============================================================================

# --- ZONES (Géospatial) ---
# IMPORTANT : ModelAdmin (Unfold) doit être cité EN PREMIER dans l'héritage.
# Python résout les attributs de gauche à droite (MRO) : si GISModelAdmin
# passe avant, ses propres templates de formulaire (carte OpenLayers)
# peuvent l'emporter sur ceux d'Unfold et cette page perd le style Tailwind.
@admin.register(Zone)
class ZoneAdmin(ModelAdmin, admin.GISModelAdmin):
    list_display = ("nom", "layer", "id_shp")
    search_fields = ("nom", "layer")
    list_filter = ("layer",)
    default_lon = -17.3100
    default_lat = 14.7900
    default_zoom = 14


# --- INLINE : PARCELLES DANS PROPRIÉTAIRE ---
class ParcelleInline(TabularInline):
    model = Parcelle
    extra = 1
    fields = ('nicad', 'zone', 'superficie', 'type_document', 'statut_fiscal', 'montant_taxe_annuelle')
    exclude = ('geom',)


# --- PROPRIETAIRES ---
@admin.register(Propriétaire)
class ProprietaireAdmin(ModelAdmin):
    list_display = ("prenom", "nom", "ni_cni", "telephone", "nb_parcelles")
    search_fields = ("nom", "prenom", "ni_cni", "telephone")
    ordering = ("nom", "prenom")
    inlines = [ParcelleInline]

    def nb_parcelles(self, obj):
        # related_name="parcelles" sur Parcelle.proprietaire (voir models.py) —
        # "parcelle_set" n'existe pas et provoquait une AttributeError ici.
        count = obj.parcelles.count()
        return format_html('<strong class="text-teal-600 font-bold">{}</strong>', count)
    nb_parcelles.short_description = "Parcelles Associées"


# --- PARCELLES ---
# Même remarque que ZoneAdmin : ModelAdmin (Unfold) en premier dans le MRO.
@admin.register(Parcelle)
class ParcelleAdmin(ModelAdmin, admin.GISModelAdmin):
    list_display = (
        "nicad",
        "proprietaire",
        "zone",
        "superficie_m2",
        "type_document",
        "badge_statut_fiscal",
        "montant_taxe_format",
    )
    list_filter = ("type_document", "statut_fiscal", "zone")
    search_fields = ("nicad", "proprietaire__nom", "proprietaire__prenom", "adresse_parcelle", "zone__nom")
    raw_id_fields = ("proprietaire",)
    default_lon = -17.3100
    default_lat = 14.7900
    default_zoom = 14

    def superficie_m2(self, obj):
        if obj.superficie is None:
            return "—"
        return f"{obj.superficie} m²"
    superficie_m2.short_description = "Superficie"

    def montant_taxe_format(self, obj):
        return fcfa(obj.montant_taxe_annuelle)
    montant_taxe_format.short_description = "Taxe Annuelle"

    def badge_statut_fiscal(self, obj):
        # Les vraies clés stockées en base sont A_JOUR / EN_RETARD / EXONERE
        # (voir Parcelle.STATUTS_FISCAUX dans models.py) — comparer avec
        # "A jour" / "En retard" ne matchait jamais, le badge affichait
        # toujours "Exonéré" par défaut quel que soit le statut réel.
        if obj.statut_fiscal == "A_JOUR":
            return format_html('<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-semibold">À jour</span>')
        elif obj.statut_fiscal == "EN_RETARD":
            return format_html('<span class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-semibold">En retard</span>')
        return format_html('<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-semibold">Exonéré</span>')
    badge_statut_fiscal.short_description = "Statut Fiscal"


# --- CONTRIBUABLES ---
@admin.register(Contribuable)
class ContribuableAdmin(ModelAdmin):
    list_display = ("numero_fiscal", "nom", "prenom", "telephone", "quartier")
    search_fields = ("numero_fiscal", "nom", "prenom", "telephone")
    list_filter = ("quartier",)


# --- TYPES DE TAXES ---
@admin.register(TypeTaxe)
class TypeTaxeAdmin(ModelAdmin):
    list_display = ("code", "libelle")
    search_fields = ("code", "libelle")


# --- TAXATIONS ---
@admin.register(Taxation)
class TaxationAdmin(ModelAdmin):
    list_display = (
        "contribuable",
        "type_taxe",
        "parcelle",
        "annee_fiscale",
        "montant_du_f",
        "montant_paye_f",
        "solde_f",
    )
    list_filter = ("annee_fiscale", "type_taxe")
    search_fields = ("contribuable__numero_fiscal", "contribuable__nom", "contribuable__prenom", "parcelle__nicad")
    raw_id_fields = ("contribuable", "parcelle")

    def montant_du_f(self, obj):
        return fcfa(obj.montant_du)
    montant_du_f.short_description = "Dû"

    def montant_paye_f(self, obj):
        return fcfa(obj.montant_paye)
    montant_paye_f.short_description = "Payé"

    def solde_f(self, obj):
        try:
            valeur_solde = obj.solde
        except Exception:
            return "—"
        if valeur_solde is None:
            return "—"
        color = "red" if valeur_solde > 0 else "green"
        # Même format (espace comme séparateur de milliers) que montant_du_f / montant_paye_f.
        texte = f"{valeur_solde:,.0f} F".replace(",", " ")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, texte)
    solde_f.short_description = "Solde"


# --- PAIEMENTS ---
@admin.register(Paiement)
class PaiementAdmin(ModelAdmin):
    list_display = ("numero_recu", "taxation", "montant_f", "date_paiement", "mode_paiement")
    list_filter = ("mode_paiement", "date_paiement")
    search_fields = ("numero_recu", "taxation__contribuable__numero_fiscal", "taxation__contribuable__nom")
    raw_id_fields = ("taxation",)
    readonly_fields = ("date_paiement", "numero_recu")

    def montant_f(self, obj):
        texte = fcfa(obj.montant)
        return format_html('<strong class="text-green-600 font-bold">{}</strong>', texte)
    montant_f.short_description = "Montant Encaissé"


# --- PROFILS CITOYENS ---
@admin.register(ProfilCitoyen)
class ProfilCitoyenAdmin(ModelAdmin):
    list_display = ("user", "contribuable", "actif", "statut_compte", "date_creation")
    list_filter = ("actif", "date_creation")
    search_fields = ("user__username", "contribuable__numero_fiscal", "contribuable__nom")
    list_editable = ("actif",)

    actions = ['activer_profils', 'desactiver_profils']

    def activer_profils(self, request, queryset):
        rows_updated = queryset.update(actif=True)
        self.message_user(request, f"✔ {rows_updated} profils citoyens ont été activés.")
    activer_profils.short_description = "✔ Activer les profils sélectionnés"

    def desactiver_profils(self, request, queryset):
        rows_updated = queryset.update(actif=False)
        self.message_user(request, f"❌ {rows_updated} profils citoyens ont été suspendus.")
    desactiver_profils.short_description = "❌ Suspendre les profils sélectionnés"

    def statut_compte(self, obj):
        if obj.actif:
            return format_html('<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-semibold">✔ Actif</span>')
        return format_html('<span class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-semibold">❌ Suspendu</span>')
    statut_compte.short_description = "Badge État"


# --- MESSAGES DE CONTACT ---
@admin.register(MessageContact)
class MessageContactAdmin(ModelAdmin):
    list_display = ("sujet", "nom", "email", "date_envoi", "badge_traite")
    list_filter = ("traite", "date_envoi")
    search_fields = ("nom", "email", "sujet", "message")
    readonly_fields = ("nom", "email", "telephone", "sujet", "message", "date_envoi")
    ordering = ("-date_envoi",)

    actions = ['marquer_traite', 'marquer_non_traite']

    def marquer_traite(self, request, queryset):
        rows_updated = queryset.update(traite=True)
        self.message_user(request, f"✔ {rows_updated} message(s) marqué(s) comme traité(s).")
    marquer_traite.short_description = "✔ Marquer comme traité"

    def marquer_non_traite(self, request, queryset):
        rows_updated = queryset.update(traite=False)
        self.message_user(request, f"↩ {rows_updated} message(s) remis en attente.")
    marquer_non_traite.short_description = "↩ Marquer comme non traité"

    def badge_traite(self, obj):
        if obj.traite:
            return format_html('<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-semibold">✔ Traité</span>')
        return format_html('<span class="bg-orange-100 text-orange-800 px-2 py-1 rounded-full text-xs font-semibold">En attente</span>')
    badge_traite.short_description = "Statut"


# --- GUIDES FISCAUX ---
@admin.register(GuideFiscal)
class GuideFiscalAdmin(ModelAdmin):
    list_display = ('sigle', 'titre', 'categorie', 'ordre')
    list_filter = ('categorie',)
    search_fields = ('titre', 'sigle')


# --- SIGNALEMENTS ---
@admin.register(Signalement)
class SignalementAdmin(ModelAdmin):
    list_display = ('titre', 'lieu', 'statut', 'date_signalement')
    list_filter = ('statut',)
    search_fields = ('titre', 'lieu', 'description')
    ordering = ('-date_signalement',)


# ==============================================================================
# 3. INFRASTRUCTURES (catégories + équipements individuels)
# ==============================================================================

# --- INLINE : INFRASTRUCTURES DANS UNE CATÉGORIE ---
class InfrastructureInline(TabularInline):
    model = Infrastructure
    extra = 1
    fields = ('nom', 'quartier', 'statut', 'latitude', 'longitude')


# --- CATÉGORIES D'INFRASTRUCTURE ---
@admin.register(CategorieInfrastructure)
class CategorieInfrastructureAdmin(ModelAdmin):
    list_display = ('label', 'code', 'icone_apercu', 'couleur_apercu', 'ordre', 'nb_infrastructures')
    list_editable = ('ordre',)
    search_fields = ('label', 'code')
    inlines = [InfrastructureInline]

    def nb_infrastructures(self, obj):
        count = obj.infrastructures.count()
        return format_html('<strong class="text-teal-600 font-bold">{}</strong>', count)
    nb_infrastructures.short_description = "Nb. infrastructures"

    def icone_apercu(self, obj):
        return format_html(
            '<i class="material-symbols-outlined" style="color:{}">•</i> <code>{}</code>',
            obj.couleur, obj.icone
        )
    icone_apercu.short_description = "Icône"

    def couleur_apercu(self, obj):
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;'
            'border-radius:4px;background:{};vertical-align:middle;margin-right:6px;"></span>{}',
            obj.couleur, obj.couleur
        )
    couleur_apercu.short_description = "Couleur"


# --- INFRASTRUCTURES ---
@admin.register(Infrastructure)
class InfrastructureAdmin(ModelAdmin):
    list_display = ('nom', 'categorie', 'quartier', 'badge_statut', 'date_ajout')
    list_filter = ('categorie', 'statut', 'quartier')
    search_fields = ('nom', 'quartier')
    list_select_related = ('categorie',)
    raw_id_fields = ('categorie',)

    def badge_statut(self, obj):
        couleurs = {
            'FONCTIONNEL':  ('bg-green-100', 'text-green-800'),
            'EN_TRAVAUX':   ('bg-orange-100', 'text-orange-800'),
            'HORS_SERVICE': ('bg-red-100', 'text-red-800'),
            'PROJETE':      ('bg-blue-100', 'text-blue-800'),
        }
        bg, text = couleurs.get(obj.statut, ('bg-gray-100', 'text-gray-800'))
        return format_html(
            '<span class="{} {} px-2 py-1 rounded-full text-xs font-semibold">{}</span>',
            bg, text, obj.get_statut_display()
        )
    badge_statut.short_description = "Statut"


# ==============================================================================
# 4. ACTUALITÉS
# ==============================================================================

@admin.register(Actualite)
class ActualiteAdmin(ModelAdmin):
    list_display = ('titre', 'categorie', 'date_publication', 'badge_publie', 'date_creation')
    list_filter = ('categorie', 'publie')
    search_fields = ('titre', 'chapo', 'contenu')
    date_hierarchy = 'date_publication'
    fields = (
        'titre', 'categorie', 'chapo', 'contenu', 'photo',
        'date_publication', 'publie',
    )

    actions = ['publier', 'depublier']

    def badge_publie(self, obj):
        if obj.publie:
            return format_html('<span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-semibold">✔ Publié</span>')
        return format_html('<span class="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs font-semibold">Brouillon</span>')
    badge_publie.short_description = "Statut"

    def publier(self, request, queryset):
        rows_updated = queryset.update(publie=True)
        self.message_user(request, f"✔ {rows_updated} actualité(s) publiée(s).")
    publier.short_description = "✔ Publier les actualités sélectionnées"

    def depublier(self, request, queryset):
        rows_updated = queryset.update(publie=False)
        self.message_user(request, f"↩ {rows_updated} actualité(s) remise(s) en brouillon.")
    depublier.short_description = "↩ Remettre en brouillon"

from .models import TypeDemande, DemandeService


@admin.register(TypeDemande)
class TypeDemandeAdmin(ModelAdmin):
    list_display = ('libelle', 'categorie', 'delai_indicatif_jours', 'necessite_parcelle', 'actif')
    list_filter = ('categorie', 'necessite_parcelle', 'actif')
    search_fields = ('libelle', 'description')


@admin.register(DemandeService)
class DemandeServiceAdmin(ModelAdmin):
    list_display = (
        'numero_dossier', 'type_demande', 'demandeur', 'parcelle',
        'statut', 'agent_traitant', 'date_demande',
    )
    list_filter = ('statut', 'type_demande__categorie', 'type_demande')
    search_fields = (
        'numero_dossier', 'demandeur__username', 'demandeur__first_name',
        'demandeur__last_name', 'objet',
    )
    autocomplete_fields = ['parcelle']
    readonly_fields = ('numero_dossier', 'date_demande', 'date_maj')