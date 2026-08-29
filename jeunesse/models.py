from django.conf import settings
from django.db import models


class ProjetJeune(models.Model):
    STATUT_EN_ATTENTE = "en_attente"
    STATUT_VALIDE = "valide"
    STATUT_REJETE = "rejete"
    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, "En attente d'étude"),
        (STATUT_VALIDE, "Validé par la mairie"),
        (STATUT_REJETE, "Non retenu"),
    ]

    SECTEUR_CHOICES = [
        ("AGRICULTURE", "Agriculture, élevage ou pêche"),
        ("COMMERCE", "Commerce"),
        ("ARTISANAT", "Artisanat"),
        ("NUMERIQUE", "Numérique et nouvelles technologies"),
        ("EDUCATION", "Éducation et formation"),
        ("SANTE", "Santé et bien-être"),
        ("ENVIRONNEMENT", "Environnement et assainissement"),
        ("CULTURE", "Culture, art et sport"),
        ("AUTRE", "Autre secteur"),
    ]

    BESOIN_CHOICES = [
        ("FINANCEMENT", "Un financement pour démarrer ou grandir"),
        ("LOCAL", "Un local ou un terrain"),
        ("FORMATION", "Une formation ou un accompagnement"),
        ("RESEAU", "Être mis en relation avec des partenaires"),
        ("MATERIEL", "Du matériel ou des équipements"),
        ("AUTRE", "Un autre besoin"),
    ]

    # Porteur de projet (pas de compte requis pour soumettre)
    nom_porteur = models.CharField("Nom complet", max_length=150)
    age = models.PositiveIntegerField("Âge", null=True, blank=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    quartier = models.CharField("Quartier à Keur Massar Nord", max_length=150, blank=True)

    # Le projet
    titre_projet = models.CharField(max_length=200)
    secteur = models.CharField(max_length=20, choices=SECTEUR_CHOICES, default="AUTRE")
    description = models.TextField()
    besoin_principal = models.CharField(max_length=20, choices=BESOIN_CHOICES, default="AUTRE")
    details_besoin = models.TextField("Précisions sur le besoin", blank=True)
    cv = models.FileField(
        "CV (PDF)", upload_to="jeunesse/cv/%Y/%m/", blank=True, null=True,
        help_text="Facultatif — format PDF, 5 Mo maximum."
    )

    # Suivi / validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="projets_jeunes_traites"
    )
    motif_rejet = models.TextField(blank=True)
    contacte = models.BooleanField("Contacté par la mairie", default=False)

    class Meta:
        verbose_name = "Projet jeune"
        verbose_name_plural = "Projets jeunes"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"{self.titre_projet} — {self.nom_porteur}"


class MessageProjet(models.Model):
    """Message envoyé par la mairie au porteur de projet (par email)."""
    projet = models.ForeignKey(ProjetJeune, on_delete=models.CASCADE, related_name="messages")
    contenu = models.TextField()
    envoye_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_envoi"]

    def __str__(self):
        return f"Message à {self.projet.nom_porteur} du {self.date_envoi:%d/%m/%Y}"


class RessourceJeune(models.Model):
    """Fiche d'information : aides, dispositifs, contacts utiles pour entreprendre."""
    CATEGORIES = [
        ("FINANCEMENT", "Financement"),
        ("FORMATION", "Formation / Accompagnement"),
        ("FONCIER", "Foncier / Local"),
        ("RESEAU", "Réseau / Partenaires"),
        ("ADMINISTRATIF", "Démarches administratives"),
    ]

    titre = models.CharField(max_length=150)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    lien = models.URLField(blank=True, help_text="Lien externe (site officiel, formulaire...)")
    contact = models.CharField(max_length=200, blank=True, help_text="Téléphone/email de contact, si utile")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Ressource jeunesse"
        verbose_name_plural = "Ressources jeunesse"
        ordering = ["categorie", "ordre", "titre"]

    def __str__(self):
        return self.titre