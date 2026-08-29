from django.conf import settings
from django.db import models


class Citoyen(models.Model):
    STATUT_EN_ATTENTE = "en_attente"
    STATUT_VALIDE = "valide"
    STATUT_REJETE = "rejete"

    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, "En attente de validation"),
        (STATUT_VALIDE, "Validé"),
        (STATUT_REJETE, "Rejeté"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="citoyen"
    )
    telephone = models.CharField("Téléphone", max_length=20, blank=True)
    numero_fiscal = models.CharField(
        "Identifiant fiscalité", max_length=50, unique=True
    )
    numero_foncier = models.CharField(
        "Identifiant foncier (NICAD)", max_length=50, unique=True
    )
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="citoyens_traites",
    )
    motif_rejet = models.TextField("Motif du rejet", blank=True)

    class Meta:
        verbose_name = "Citoyen"
        verbose_name_plural = "Citoyens"
        ordering = ["-date_inscription"]

    def __str__(self):
        nom = self.user.get_full_name() or self.user.username
        return f"{nom} ({self.get_statut_display()})"

    @property
    def est_valide(self):
        return self.statut == self.STATUT_VALIDE

    @property
    def est_en_attente(self):
        return self.statut == self.STATUT_EN_ATTENTE