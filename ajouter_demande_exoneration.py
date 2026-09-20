CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

class DemandeExoneration(models.Model):
    """
    Demande d'exoneration fiscale pour une parcelle : le contribuable
    estime que son bien devrait etre exempte de taxe fonciere (batiment
    religieux, etablissement public, mission diplomatique...). Si
    validee, le statut fiscal de la parcelle passe a EXONERE, et la
    commande emettre_role_annuel ne lui emettra plus de nouvelle
    taxation pour les annees suivantes.
    """
    MOTIF_RELIGIEUX = "RELIGIEUX"
    MOTIF_PUBLIC = "PUBLIC"
    MOTIF_DIPLOMATIQUE = "DIPLOMATIQUE"
    MOTIF_AUTRE = "AUTRE"
    MOTIF_CHOICES = [
        (MOTIF_RELIGIEUX, "Bâtiment religieux (mosquée, église...)"),
        (MOTIF_PUBLIC, "Établissement public (école, hôpital, administration...)"),
        (MOTIF_DIPLOMATIQUE, "Mission diplomatique"),
        (MOTIF_AUTRE, "Autre motif"),
    ]

    STATUT_SOUMISE = "SOUMISE"
    STATUT_EN_EXAMEN = "EN_EXAMEN"
    STATUT_VALIDEE = "VALIDEE"
    STATUT_REJETEE = "REJETEE"
    STATUT_CHOICES = [
        (STATUT_SOUMISE, "Soumise"),
        (STATUT_EN_EXAMEN, "En cours d'examen"),
        (STATUT_VALIDEE, "Validée"),
        (STATUT_REJETEE, "Rejetée"),
    ]

    contribuable = models.ForeignKey(
        Contribuable, on_delete=models.CASCADE, related_name="demandes_exoneration"
    )
    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.CASCADE, related_name="demandes_exoneration"
    )

    motif = models.CharField(max_length=20, choices=MOTIF_CHOICES)
    description = models.TextField(
        blank=True, verbose_name="Précisions",
        help_text="Détaillez votre situation si besoin (surtout pour 'Autre motif').",
    )
    piece_jointe = models.FileField(
        upload_to="exonerations/",
        help_text="Justificatif (attestation religieuse, arrêté, décision administrative...).",
    )

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMISE)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="exonerations_traitees",
    )
    motif_rejet = models.TextField(blank=True)

    class Meta:
        verbose_name = "Demande d'exonération"
        verbose_name_plural = "Demandes d'exonération"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"{self.parcelle.nicad} — {self.get_motif_display()} ({self.get_statut_display()})"
'''

if "class DemandeExoneration" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : modele DemandeExoneration ajoute a la fin du fichier.")