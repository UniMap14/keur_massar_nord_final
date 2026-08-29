from django.db import models
import uuid

# Create your models here.
from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Zone(models.Model):
    """Modèle pour représenter les zones/quartiers du shapefile importé."""
    id_shp = models.BigIntegerField(unique=True, verbose_name="ID du shapefile")
    nom = models.CharField(max_length=255, verbose_name="Nom de la zone/quartier")
    layer = models.CharField(max_length=100, verbose_name="Couche du shapefile")
    path = models.CharField(max_length=255, verbose_name="Chemin du fichier source")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie de la zone")
    
    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.layer})"


class Propriétaire(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    ni_cni = models.CharField(max_length=20, unique=True, verbose_name="Numéro CNI")
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Parcelle(models.Model):
    TYPES_DOCUMENT = [
        ('TF', 'Titre Foncier'),
        ('BAIL', 'Bail'),
        ('DELIB', 'Délibération Municipale'),
        ('ATTES', 'Attestation de cession'),
    ]

    STATUTS_FISCAUX = [
        ('A_JOUR', 'À Jour'),
        ('EN_RETARD', 'En Retard de Paiement'),
        ('EXONERE', 'Exonéré'),
    ]

    nicad = models.CharField(max_length=50, verbose_name="Numéro NICAD / Lot")
    id_shp = models.CharField(
        max_length=20, unique=True, blank=True, null=True,
        verbose_name="ID unique (import shapefile)",
        help_text="Identifiant du polygone source (ex: KMN-000001), pour éviter les doublons lors d'un ré-import.",
    )
    proprietaire = models.ForeignKey(Propriétaire, on_delete=models.SET_NULL, null=True, related_name="parcelles")
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name="parcelles", verbose_name="Zone/Quartier")
    superficie = models.FloatField(help_text="Superficie en mètres carrés")
    type_document = models.CharField(max_length=10, choices=TYPES_DOCUMENT, default='DELIB')
    adresse_parcelle = models.CharField(max_length=255, blank=True, help_text="Quartier ou secteur à Keur Massar Nord")

    # --- Ajoutés pour l'import du shapefile arrete_kms_008_003_014_final ---
    reference_arrete = models.CharField(max_length=100, blank=True, verbose_name="Référence de l'arrêté")
    occupation_sol = models.CharField(max_length=150, blank=True, verbose_name="Occupation du sol")

    # --- SECTION FISCALE ---
    valeur_locative = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Valeur estimée en FCFA")
    montant_taxe_annuelle = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="CFPB annuelle en FCFA")
    statut_fiscal = models.CharField(max_length=15, choices=STATUTS_FISCAUX, default='A_JOUR')

    # --- SECTION GÉOGRAPHIQUE (POSTGIS) ---
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f"Parcelle {self.nicad} - {self.adresse_parcelle}"

# =========================================
# MODULE FISCALITÉ COMMUNALE
# (distinct de la fiscalité nationale présentée
# à titre informatif dans les autres onglets)
# =========================================

class Contribuable(models.Model):
    """
    Une personne redevable de taxes communales. Peut être liée à un
    Propriétaire (cas d'une taxe foncière) mais pas obligatoirement
    (ex : patente d'un commerçant qui loue son local).
    """
    proprietaire = models.ForeignKey(
        Propriétaire, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contribuables"
    )
    numero_fiscal = models.CharField(max_length=30, unique=True, verbose_name="Numéro fiscal communal")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    quartier = models.CharField(max_length=100, blank=True, help_text="Quartier de résidence ou d'activité")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contribuable"
        verbose_name_plural = "Contribuables"

    def __str__(self):
        return f"{self.numero_fiscal} — {self.nom} {self.prenom}".strip()

    @property
    def parcelles_display(self):
        nicads = (
            self.taxations.exclude(parcelle__isnull=True)
            .values_list('parcelle__nicad', flat=True)
            .distinct()
        )
        return ", ".join(nicads) or "—"

    @property
    def montant_du_total(self):
        return self.taxations.aggregate(total=models.Sum('montant_du'))['total'] or 0

    @property
    def montant_paye_total(self):
        return Paiement.objects.filter(
            taxation__contribuable=self, statut_paiement='CONFIRME'
        ).aggregate(
            total=models.Sum('montant')
        )['total'] or 0

    @property
    def solde_total(self):
        return self.montant_du_total - self.montant_paye_total

    @property
    def statut_global(self):
        return 'A_JOUR' if self.solde_total <= 0 else 'EN_RETARD'


class TypeTaxe(models.Model):
    """Les taxes propres à la commune (distinctes des impôts nationaux DGID)."""
    CODES = [
        ('FONCIERE', 'Taxe foncière communale'),
        ('PATENTE', 'Patente locale'),
        ('OCCUPATION', "Taxe d'occupation"),
        ('MARCHE', 'Taxe sur les marchés'),
        ('ASSAINISSEMENT', "Redevance d'assainissement"),
        ('PUBLICITE', 'Taxe sur la publicité'),
    ]
    MOIS_CHOICES = [
        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
        (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
    ]

    code = models.CharField(max_length=20, choices=CODES, unique=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    mois_echeance = models.PositiveSmallIntegerField(
        "Mois de l'échéance annuelle", choices=MOIS_CHOICES, null=True, blank=True,
        help_text="Mois de la date limite de paiement (se répète chaque année)."
    )
    jour_echeance = models.PositiveSmallIntegerField(
        "Jour de l'échéance", null=True, blank=True,
        help_text="Jour du mois (1 à 31)."
    )
    penalite_retard = models.CharField(
        "Pénalité de retard", max_length=150, blank=True,
        help_text="Ex : « Majoration de 10% après la date limite »."
    )

    class Meta:
        verbose_name = "Type de taxe"
        verbose_name_plural = "Types de taxe"

    def __str__(self):
        return self.libelle

    def prochaine_echeance(self):
        """
        Renvoie la prochaine date limite de paiement (objet date), en
        reportant sur l'année suivante si la date de cette année est déjà
        passée. Renvoie None si aucune échéance n'est configurée.
        """
        if not self.mois_echeance or not self.jour_echeance:
            return None
        import datetime
        aujourdhui = datetime.date.today()
        annee = aujourdhui.year
        try:
            echeance = datetime.date(annee, self.mois_echeance, self.jour_echeance)
        except ValueError:
            # Jour invalide pour ce mois (ex: 31 février) : on retombe sur
            # le dernier jour du mois concerné.
            import calendar
            dernier_jour = calendar.monthrange(annee, self.mois_echeance)[1]
            echeance = datetime.date(annee, self.mois_echeance, dernier_jour)
        if echeance < aujourdhui:
            try:
                echeance = datetime.date(annee + 1, self.mois_echeance, self.jour_echeance)
            except ValueError:
                import calendar
                dernier_jour = calendar.monthrange(annee + 1, self.mois_echeance)[1]
                echeance = datetime.date(annee + 1, self.mois_echeance, dernier_jour)
        return echeance

    def jours_restants(self):
        """Nombre de jours avant la prochaine échéance, ou None si non configurée."""
        echeance = self.prochaine_echeance()
        if echeance is None:
            return None
        import datetime
        return (echeance - datetime.date.today()).days


class Taxation(models.Model):
    """Une taxe due par un contribuable, pour une année fiscale donnée."""
    contribuable = models.ForeignKey(Contribuable, on_delete=models.CASCADE, related_name="taxations")
    type_taxe = models.ForeignKey(TypeTaxe, on_delete=models.PROTECT, related_name="taxations")
    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.SET_NULL, null=True, blank=True, related_name="taxations"
    )
    annee_fiscale = models.PositiveIntegerField()
    montant_du = models.DecimalField(max_digits=12, decimal_places=2)
    date_emission = models.DateField(auto_now_add=True)
    dernier_rappel_envoye = models.DateField(
        blank=True, null=True,
        verbose_name="Dernier rappel d'échéance envoyé",
        help_text="Rempli automatiquement par la commande envoyer_rappels_echeances, pour ne jamais envoyer deux fois le même rappel.",
    )

    class Meta:
        verbose_name = "Taxation"
        verbose_name_plural = "Taxations"
        unique_together = ('contribuable', 'type_taxe', 'annee_fiscale', 'parcelle')
        ordering = ['-annee_fiscale']

    def __str__(self):
        return f"{self.type_taxe} {self.annee_fiscale} — {self.contribuable}"

    @property
    def montant_paye(self):
        return (
            self.paiements
            .filter(statut_paiement='CONFIRME')
            .aggregate(total=models.Sum('montant'))['total']
            or 0
        )

    @property
    def solde(self):
        return self.montant_du - self.montant_paye

    @property
    def statut(self):
        return 'A_JOUR' if self.solde <= 0 else 'EN_RETARD'


class Paiement(models.Model):
    MODES = [
        ('ESPECES', 'Espèces (guichet)'),
        ('MOBILE', 'Mobile Money'),
        ('VIREMENT', 'Virement bancaire'),
        ('CHEQUE', 'Chèque'),
    ]
    STATUTS_PAIEMENT = [
        ('CONFIRME', 'Confirmé'),
        ('EN_ATTENTE', 'En attente de confirmation'),
        ('ECHEC', 'Échoué'),
    ]
    taxation = models.ForeignKey(Taxation, on_delete=models.CASCADE, related_name="paiements")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_paiement = models.DateField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=15, choices=MODES, default='ESPECES')
    numero_recu = models.CharField(max_length=30, unique=True, blank=True)
    statut_paiement = models.CharField(
        max_length=15, choices=STATUTS_PAIEMENT, default='CONFIRME',
        help_text="Un paiement au guichet est confirmé immédiatement. Un paiement en "
                   "ligne (Orange Money/Wave) reste 'En attente' jusqu'à la confirmation "
                   "de l'opérateur.",
    )
    reference_transaction = models.CharField(
        max_length=100, blank=True, default='',
        help_text="Identifiant de transaction donné par l'opérateur de paiement en ligne (le cas échéant).",
    )

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']

    def save(self, *args, **kwargs):
        if not self.numero_recu:
            import uuid
            annee = self.date_paiement.year if self.date_paiement else __import__('datetime').date.today().year
            self.numero_recu = f"KMSN-{annee}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero_recu
class ProfilCitoyen(models.Model):
    """
    Lie un compte Django à un contribuable.
    Chaque contribuable possède un seul compte.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profil_citoyen"
    )

    contribuable = models.OneToOneField(
        Contribuable,
        on_delete=models.CASCADE,
        related_name="profil"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.contribuable.nom} {self.contribuable.prenom}"
# =========================================
# FORMULAIRE DE CONTACT
# =========================================

class MessageContact(models.Model):
    """Message envoyé via le formulaire de contact public du site."""

    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    sujet = models.CharField(max_length=150)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False, verbose_name="Traité")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.sujet} — {self.nom} ({self.date_envoi:%d/%m/%Y})"
class GuideFiscal(models.Model):
    """Fiches d'information fiscale et foncière (basées sur la documentation DGID)."""

    CATEGORIES = [
        ('IMPOTS_DIRECTS', 'Impôts directs'),
        ('CONTRIBUTIONS_LOCALES', 'Contributions locales'),
        ('FONCIER_CADASTRE', 'Foncier & Cadastre'),
        ('DEMARCHES', 'Démarches administratives'),
    ]

    code = models.SlugField(max_length=50, unique=True, help_text="Identifiant court, ex: 'is', 'ir', 'cfpb'")
    sigle = models.CharField(max_length=20, blank=True, help_text="Ex: IS, IR, CFPB, NICAD")
    titre = models.CharField(max_length=150)
    categorie = models.CharField(max_length=25, choices=CATEGORIES)
    resume = models.CharField(max_length=300, help_text="Phrase courte affichée dans la liste")

    qui_est_concerne = models.TextField(blank=True)
    taux_et_calcul = models.TextField(blank=True)
    modalites_declaration = models.TextField(blank=True)
    sanctions = models.TextField(blank=True)
    references_legales = models.TextField(blank=True)

    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Guide fiscal"
        verbose_name_plural = "Guides fiscaux"
        ordering = ['ordre', 'titre']

    def __str__(self):
        return f"{self.sigle} — {self.titre}" if self.sigle else self.titre
# ============================================================
# À COPIER DANS : foncier/models.py (à la suite de tes modèles existants)
# ============================================================


class Signalement(models.Model):
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lieu = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='signalements/', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_COURS')
    date_signalement = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    commentaire_agent = models.TextField(
        blank=True,
        default='',
        verbose_name="Note interne (agent)",
        help_text="Visible uniquement par l'administration, jamais par le public.",
    )
    reference = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Code de suivi",
        help_text="Identifiant secret donné au citoyen pour suivre son signalement, sans compte.",
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone (optionnel)",
        help_text="Si renseigné : un SMS est envoyé au citoyen quand le signalement est résolu.",
    )
    agent_assigne = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name="signalements_assignes",
        verbose_name="Agent assigné",
    )

    class Meta:
        ordering = ['-date_signalement']
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"

    def __str__(self):
        return self.titre


# Optionnel : si tu veux gérer les catégories d'infrastructures depuis l'admin
# plutôt qu'en dur dans la vue (voir views_additions.py), décommente ceci :
#
# class CategorieInfrastructure(models.Model):
#     label = models.CharField(max_length=100)          # ex: "Écoles"
#     icone = models.CharField(max_length=50)            # ex: "fa-graduation-cap"
#     total = models.PositiveIntegerField(default=0)
#     ordre = models.PositiveIntegerField(default=0)
#
#     class Meta:
#         ordering = ['ordre']
#
#     def __str__(self):
#         return self.label
# ============================================================
# À AJOUTER DANS : foncier/models.py
# (remplace le bloc commenté "CategorieInfrastructure" à la fin du fichier)
# ============================================================

class CategorieInfrastructure(models.Model):
    """Une catégorie d'équipement public/privé (Éducation, Santé, Voirie...)."""

    code = models.SlugField(
        max_length=50, unique=True,
        help_text="Identifiant court, ex: 'education', 'sante', 'voirie'"
    )
    label = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.CharField(
        max_length=255, blank=True,
        help_text="Sous-titre affiché sous le nom, ex: 'Écoles, CEM, lycées...'"
    )
    texte_intro = models.TextField(
        blank=True,
        help_text="Paragraphe d'introduction affiché en haut du panneau détaillé"
    )
    icone = models.CharField(
        max_length=50, default='fa-map-pin',
        help_text="Classe FontAwesome sans le préfixe 'fa-solid', ex: 'fa-school'"
    )
    couleur = models.CharField(
        max_length=20, default='#2f7a4f',
        help_text="Couleur hexadécimale utilisée pour l'icône et les accents"
    )
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Catégorie d'infrastructure"
        verbose_name_plural = "Catégories d'infrastructure"
        ordering = ['ordre', 'label']

    def __str__(self):
        return self.label


class Infrastructure(models.Model):
    """Un équipement individuel recensé (une école précise, un forage précis...)."""

    STATUTS = [
        ('FONCTIONNEL', 'Fonctionnel'),
        ('EN_TRAVAUX', 'En travaux / réhabilitation'),
        ('HORS_SERVICE', 'Hors service'),
        ('PROJETE', 'Projeté'),
    ]

    categorie = models.ForeignKey(
        CategorieInfrastructure, on_delete=models.CASCADE,
        related_name='infrastructures'
    )
    nom = models.CharField(max_length=200)
    quartier = models.CharField(max_length=150, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='FONCTIONNEL')

    # Coordonnées facultatives, pour un jour les afficher sur le géoportail
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    notes = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Infrastructure"
        verbose_name_plural = "Infrastructures"
        ordering = ['categorie__ordre', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.categorie.label})"
# ============================================================
# À AJOUTER DANS : foncier/models.py (à la fin du fichier)
# ============================================================

class Actualite(models.Model):
    """Avis, communiqués, projets et appels d'offres publiés sur l'accueil."""

    CATEGORIES = [
        ('AVIS', 'Avis'),
        ('PROJET', 'Projet'),
        ('COMMUNIQUE', 'Communiqué'),
        ('APPEL_OFFRES', "Appel d'offres"),
        ('EVENEMENT', 'Événement'),
    ]

    titre = models.CharField(max_length=200)
    chapo = models.TextField(
        max_length=400,
        help_text="Court résumé affiché sur la carte de l'accueil (quelques phrases)."
    )
    contenu = models.TextField(
        blank=True,
        help_text="Texte complet de l'article, si vous voulez une page de détail."
    )
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='AVIS')
    photo = models.ImageField(upload_to='actualites/', blank=True, null=True)

    date_publication = models.DateField(verbose_name="Date à afficher")
    date_creation = models.DateTimeField(auto_now_add=True)

    publie = models.BooleanField(
        default=True,
        verbose_name="Publié",
        help_text="Décochez pour garder l'article en brouillon (invisible sur le site)."
    )

    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ['-date_publication', '-date_creation']

    def __str__(self):
        return self.titre

from django.utils import timezone
from django.conf import settings as django_settings
from django.core.files.storage import FileSystemStorage

# Stockage PRIVÉ pour les pièces jointes des démarches : écrit dans
# PRIVATE_MEDIA_ROOT (hors de MEDIA_ROOT), donc jamais accessible via une
# URL /media/... publique. Le seul accès possible passe par la vue
# authentifiée citoyens.views.demande_piece_jointe_view.
stockage_pieces_jointes = FileSystemStorage(
    location=str(django_settings.PRIVATE_MEDIA_ROOT / "demandes"),
    base_url=None,
)


class TypeDemande(models.Model):
    """
    Référentiel des démarches administratives/cadastrales que la commune
    propose en ligne (ex : extrait cadastral, certificat de résidence,
    autorisation d'occuper le sol...).
    """
    CATEGORIES = [
        ('CADASTRE', 'Cadastre / Foncier'),
        ('ETAT_CIVIL', 'État civil'),
        ('URBANISME', 'Urbanisme / Construction'),
        ('FISCALITE', 'Fiscalité'),
        ('AUTRE', 'Autre'),
    ]

    libelle = models.CharField(max_length=150)
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='CADASTRE')
    description = models.TextField(blank=True, help_text="Ce que couvre cette démarche.")
    pieces_requises = models.TextField(
        blank=True,
        help_text="Liste des pièces à fournir (une par ligne)."
    )
    delai_indicatif_jours = models.PositiveIntegerField(default=5)
    necessite_parcelle = models.BooleanField(
        default=False,
        help_text="Cocher si cette démarche concerne une parcelle précise (ex : extrait cadastral)."
    )
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Type de démarche"
        verbose_name_plural = "Types de démarche"
        ordering = ['categorie', 'libelle']

    def __str__(self):
        return self.libelle


class DemandeService(models.Model):
    """Une demande de démarche administrative/cadastrale déposée par un citoyen."""

    STATUT_RECUE = 'RECUE'
    STATUT_EN_COURS = 'EN_COURS'
    STATUT_PRETE = 'PRETE'
    STATUT_REJETEE = 'REJETEE'
    STATUT_CLOTUREE = 'CLOTUREE'

    STATUT_CHOICES = [
        (STATUT_RECUE, 'Reçue'),
        (STATUT_EN_COURS, 'En cours de traitement'),
        (STATUT_PRETE, 'Prête à retirer'),
        (STATUT_REJETEE, 'Rejetée'),
        (STATUT_CLOTUREE, 'Clôturée'),
    ]

    numero_dossier = models.CharField(max_length=30, unique=True, blank=True)
    demandeur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="demandes_service"
    )
    type_demande = models.ForeignKey(
        TypeDemande, on_delete=models.PROTECT, related_name="demandes"
    )
    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="demandes_service"
    )
    objet = models.TextField("Précisions sur la demande", blank=True)
    piece_jointe = models.FileField(upload_to='', blank=True, null=True, storage=stockage_pieces_jointes)

    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default=STATUT_RECUE)
    commentaire_agent = models.TextField(blank=True)
    agent_traitant = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="demandes_traitees"
    )

    date_demande = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de service"
        verbose_name_plural = "Demandes de service"
        ordering = ['-date_demande']

    def save(self, *args, **kwargs):
        if not self.numero_dossier:
            import uuid
            annee = timezone.now().year
            self.numero_dossier = f"KMSN-DS-{annee}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_dossier} — {self.type_demande}"


class JournalAudit(models.Model):
    """
    Journal d'audit : trace qui a modifié quoi et quand, sur les
    modèles sensibles (Parcelle, Taxation, Paiement, Contribuable,
    Signalement, DemandeService). Rempli automatiquement par des
    signaux Django (voir foncier/audit.py) — jamais modifié à la main.
    """
    ACTION_CHOICES = [
        ('CREATION', 'Création'),
        ('MODIFICATION', 'Modification'),
        ('SUPPRESSION', 'Suppression'),
    ]

    horodatage = models.DateTimeField(auto_now_add=True, db_index=True)
    utilisateur = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name="actions_audit",
    )
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    modele = models.CharField(max_length=50, db_index=True)
    objet_id = models.CharField(max_length=30)
    objet_repr = models.CharField(
        max_length=255,
        help_text="Description de l'objet au moment de l'action (reste lisible même si l'objet est ensuite supprimé).",
    )
    champs_modifies = models.JSONField(
        blank=True, null=True,
        help_text="Pour une modification : {'champ': ['ancienne valeur', 'nouvelle valeur']}.",
    )
    adresse_ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = "Entrée du journal d'audit"
        verbose_name_plural = "Journal d'audit"
        ordering = ['-horodatage']

    def __str__(self):
        return f"{self.get_action_display()} — {self.modele} #{self.objet_id} par {self.utilisateur or 'système'}"