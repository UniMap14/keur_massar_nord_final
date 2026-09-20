CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

class DemandeImmatriculation(models.Model):
    """
    Demande de premiere immatriculation fiscale : une personne qui n'a
    jamais ete contribuable (ex : vient d'acheter un bien) demande a
    etre enregistree pour une parcelle deja cadastree mais pas encore
    rattachee a un proprietaire/contribuable connu. Principe de
    l'adhesion SenTax, transpose a la fiscalite fonciere locale.
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

    OCCUPATIONS = [
        ("Terrain Nu", "Terrain Nu"),
        ("Bâti", "Bâti"),
        ("Zone de culture", "Zone de culture"),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    ni_cni = models.CharField("Numéro CNI", max_length=20)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.CASCADE, related_name="demandes_immatriculation"
    )
    occupation_declaree = models.CharField(max_length=30, choices=OCCUPATIONS)
    piece_jointe = models.FileField(
        upload_to="immatriculations/",
        help_text="Acte de vente, titre foncier ou attestation de cession (obligatoire).",
    )

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMISE)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="immatriculations_traitees",
    )
    motif_rejet = models.TextField(blank=True)

    contribuable_cree = models.ForeignKey(
        Contribuable, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="demande_origine",
    )

    class Meta:
        verbose_name = "Demande de première immatriculation"
        verbose_name_plural = "Demandes de première immatriculation"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"{self.nom} {self.prenom} — {self.parcelle.nicad} ({self.get_statut_display()})"
'''

if "class DemandeImmatriculation" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : modele DemandeImmatriculation ajoute a la fin du fichier.")