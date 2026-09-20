CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

class RecoursFiscal(models.Model):
    """
    Contestation d'une taxation par le contribuable (recours simple,
    niveau 1), avec une possibilite de suivi en REDRESSEMENT (niveau 2)
    si le recours initial est rejete : le contribuable demande alors au
    Chef Fiscalite de verifier specifiquement l'historique de ses
    paiements des mois/annees precedents, pour prouver sa bonne foi.
    Reste traite par le meme role (fiscal), contrairement a un recours
    hierarchique classique.
    """
    NIVEAU_RECOURS = 1
    NIVEAU_REDRESSEMENT = 2
    NIVEAU_CHOICES = [
        (NIVEAU_RECOURS, "Recours (contestation initiale)"),
        (NIVEAU_REDRESSEMENT, "Redressement (vérification de l'historique des paiements)"),
    ]

    STATUT_SOUMIS = "SOUMIS"
    STATUT_EN_EXAMEN = "EN_EXAMEN"
    STATUT_ACCEPTE = "ACCEPTE"
    STATUT_REJETE = "REJETE"
    STATUT_CHOICES = [
        (STATUT_SOUMIS, "Soumis"),
        (STATUT_EN_EXAMEN, "En cours d'examen"),
        (STATUT_ACCEPTE, "Accepté"),
        (STATUT_REJETE, "Rejeté"),
    ]

    taxation = models.ForeignKey(Taxation, on_delete=models.CASCADE, related_name="recours")
    contribuable = models.ForeignKey(Contribuable, on_delete=models.CASCADE, related_name="recours_fiscaux")

    niveau = models.PositiveSmallIntegerField(choices=NIVEAU_CHOICES, default=NIVEAU_RECOURS)
    recours_precedent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="redressement"
    )

    motif = models.TextField(verbose_name="Motif de la contestation")
    piece_jointe = models.FileField(upload_to="recours_fiscaux/", blank=True, null=True)

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMIS)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="recours_traites"
    )
    decision_commentaire = models.TextField(blank=True, verbose_name="Explication de la décision")
    ancien_montant = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    nouveau_montant = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Recours fiscal"
        verbose_name_plural = "Recours fiscaux"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"{self.get_niveau_display()} — {self.taxation} ({self.get_statut_display()})"
'''

if "class RecoursFiscal" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : modele RecoursFiscal ajoute a la fin du fichier.")