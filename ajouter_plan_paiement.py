CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

class PlanPaiement(models.Model):
    """
    Demande d'echelonnement d'une taxation en plusieurs echeances (au
    lieu d'un paiement unique). Une fois validee, genere automatiquement
    les EcheancePlanPaiement correspondantes (montants egaux, dates
    espacees d'un mois).
    """
    STATUT_SOUMIS = "SOUMIS"
    STATUT_EN_EXAMEN = "EN_EXAMEN"
    STATUT_VALIDE = "VALIDE"
    STATUT_REJETE = "REJETE"
    STATUT_TERMINE = "TERMINE"
    STATUT_CHOICES = [
        (STATUT_SOUMIS, "Soumis"),
        (STATUT_EN_EXAMEN, "En cours d'examen"),
        (STATUT_VALIDE, "Validé"),
        (STATUT_REJETE, "Rejeté"),
        (STATUT_TERMINE, "Terminé (toutes échéances payées)"),
    ]

    taxation = models.ForeignKey(
        Taxation, on_delete=models.CASCADE, related_name="plans_paiement"
    )
    contribuable = models.ForeignKey(
        Contribuable, on_delete=models.CASCADE, related_name="plans_paiement"
    )
    nombre_echeances = models.PositiveSmallIntegerField(
        verbose_name="Nombre d'échéances souhaité",
        help_text="Entre 2 et 4 échéances.",
    )
    motif = models.TextField(verbose_name="Motif de la demande")

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMIS)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="plans_paiement_traites",
    )
    motif_rejet = models.TextField(blank=True)

    class Meta:
        verbose_name = "Plan de paiement"
        verbose_name_plural = "Plans de paiement"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"Plan {self.taxation} en {self.nombre_echeances} échéance(s) ({self.get_statut_display()})"


class EcheancePlanPaiement(models.Model):
    """Une echeance individuelle d'un plan de paiement valide."""
    STATUT_EN_ATTENTE = "EN_ATTENTE"
    STATUT_PAYEE = "PAYEE"
    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, "En attente"),
        (STATUT_PAYEE, "Payée"),
    ]

    plan = models.ForeignKey(PlanPaiement, on_delete=models.CASCADE, related_name="echeances")
    numero = models.PositiveSmallIntegerField(verbose_name="N° de l'échéance")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_prevue = models.DateField()
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE)
    paiement = models.ForeignKey(
        Paiement, on_delete=models.SET_NULL, null=True, blank=True, related_name="echeance_origine"
    )

    class Meta:
        verbose_name = "Échéance de plan de paiement"
        verbose_name_plural = "Échéances de plan de paiement"
        ordering = ["plan", "numero"]

    def __str__(self):
        return f"Échéance {self.numero} — {self.montant} FCFA ({self.get_statut_display()})"
'''

if "class PlanPaiement" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : modeles PlanPaiement + EcheancePlanPaiement ajoutes a la fin du fichier.")