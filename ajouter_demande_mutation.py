CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

class DemandeMutation(models.Model):
    """
    Demande de mutation fiscale : transfert du dossier fiscal d'une
    parcelle deja rattachee a un proprietaire, vers un nouveau
    proprietaire (typiquement suite a une revente). Deposee
    publiquement par l'acheteur, avec preuve d'achat. Cree un nouveau
    Contribuable pour l'acheteur a la validation, et rattache la
    parcelle a son nouveau proprietaire.
    """
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

    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.CASCADE, related_name="demandes_mutation"
    )

    nouveau_nom = models.CharField("Nom du nouveau propriétaire", max_length=100)
    nouveau_prenom = models.CharField("Prénom du nouveau propriétaire", max_length=100)
    nouveau_cni = models.CharField("Numéro CNI du nouveau propriétaire", max_length=20)
    nouveau_telephone = models.CharField("Téléphone", max_length=20)
    nouveau_email = models.EmailField("Email (facultatif)", blank=True)

    piece_jointe = models.FileField(
        upload_to="mutations/",
        help_text="Acte de vente ou tout document attestant du transfert de propriété (obligatoire).",
    )

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMISE)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="mutations_traitees",
    )
    motif_rejet = models.TextField(blank=True)

    nouveau_contribuable_cree = models.ForeignKey(
        Contribuable, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="mutation_origine",
    )

    class Meta:
        verbose_name = "Demande de mutation fiscale"
        verbose_name_plural = "Demandes de mutation fiscale"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"Mutation {self.parcelle.nicad} → {self.nouveau_nom} {self.nouveau_prenom} ({self.get_statut_display()})"
'''

if "class DemandeMutation" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : modele DemandeMutation ajoute a la fin du fichier.")