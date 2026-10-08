CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

class DemandeMorcellementFusion(models.Model):
    """
    Demande de morcellement (division d'une parcelle en plusieurs) ou
    de fusion (regroupement de plusieurs parcelles en une seule).

    - FUSION : la nouvelle geometrie est calculee automatiquement
      (union des contours existants) a la validation.
    - MORCELLEMENT : la decoupe geometrique precise necessite le plan
      d'un geometre-expert (piece jointe obligatoire) -- l'agent cree
      manuellement les nouvelles parcelles (via l'admin, ou en leur
      liant cette demande via 'demande_origine') avant de cloturer.
    """
    TYPE_MORCELLEMENT = "MORCELLEMENT"
    TYPE_FUSION = "FUSION"
    TYPE_CHOICES = [
        (TYPE_MORCELLEMENT, "Morcellement (diviser une parcelle)"),
        (TYPE_FUSION, "Fusion (regrouper plusieurs parcelles)"),
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

    demandeur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="demandes_morcellement_fusion"
    )
    type_operation = models.CharField(max_length=15, choices=TYPE_CHOICES)
    parcelles_concernees = models.ManyToManyField(
        Parcelle, related_name="demandes_morcellement_fusion_origine"
    )
    justification = models.TextField(verbose_name="Motif de la demande")
    piece_jointe = models.FileField(
        upload_to="morcellement_fusion/",
        help_text="Plan du géomètre-expert ou tout document justificatif (obligatoire).",
    )

    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default=STATUT_SOUMISE)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="morcellements_fusions_traites",
    )
    motif_rejet = models.TextField(blank=True)

    class Meta:
        verbose_name = "Demande de morcellement/fusion"
        verbose_name_plural = "Demandes de morcellement/fusion"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"{self.get_type_operation_display()} — {self.get_statut_display()}"
'''

if "class DemandeMorcellementFusion" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : modele DemandeMorcellementFusion ajoute a la fin du fichier.")