CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

class DeclarationFiscale(models.Model):
    """
    Declaration faite par un citoyen pour une parcelle et une annee
    fiscale donnee : il declare l'occupation reelle du terrain (Terrain
    Nu, Bati, Zone de culture...), sur laquelle l'administration s'appuie
    pour calculer et emettre la taxation correspondante. Reprend le
    principe de la teledeclaration SenTax (le contribuable declare,
    un agent valide ou rejette), applique a la fiscalite fonciere locale.
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

    contribuable = models.ForeignKey(
        Contribuable, on_delete=models.CASCADE, related_name="declarations"
    )
    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.CASCADE, related_name="declarations"
    )
    type_taxe = models.ForeignKey(
        TypeTaxe, on_delete=models.PROTECT, related_name="declarations"
    )
    annee_fiscale = models.PositiveIntegerField()

    occupation_declaree = models.CharField(max_length=30, choices=OCCUPATIONS)
    superficie_declaree = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Laisser vide pour reprendre la superficie cadastrale."
    )
    commentaire_citoyen = models.TextField(blank=True, verbose_name="Précisions apportées")
    piece_jointe = models.FileField(upload_to="declarations_fiscales/", blank=True, null=True)

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMISE)
    date_declaration = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="declarations_traitees"
    )
    motif_rejet = models.TextField(blank=True)
    commentaire_agent = models.TextField(blank=True)

    taxation_generee = models.ForeignKey(
        Taxation, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="declaration_origine"
    )

    class Meta:
        verbose_name = "Déclaration fiscale"
        verbose_name_plural = "Déclarations fiscales"
        ordering = ["-date_declaration"]

    def __str__(self):
        return f"Déclaration {self.parcelle.nicad} - {self.annee_fiscale} ({self.get_statut_display()})"
'''

if "class DeclarationFiscale" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : modele DeclarationFiscale ajoute a la fin du fichier.")