CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    piece_jointe = models.FileField(upload_to='', blank=True, null=True, storage=stockage_pieces_jointes)

    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default=STATUT_RECUE)'''

nouveau = '''    piece_jointe = models.FileField(upload_to='', blank=True, null=True, storage=stockage_pieces_jointes)

    STATUT_PAIEMENT_NON_REQUIS = "NON_REQUIS"
    STATUT_PAIEMENT_EN_ATTENTE = "EN_ATTENTE"
    STATUT_PAIEMENT_CONFIRME = "CONFIRME"
    STATUT_PAIEMENT_CHOICES = [
        (STATUT_PAIEMENT_NON_REQUIS, "Non requis (démarche gratuite)"),
        (STATUT_PAIEMENT_EN_ATTENTE, "En attente de validation"),
        (STATUT_PAIEMENT_CONFIRME, "Confirmé"),
    ]
    statut_paiement = models.CharField(
        max_length=15, choices=STATUT_PAIEMENT_CHOICES, default=STATUT_PAIEMENT_NON_REQUIS
    )
    montant_paye = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    reference_paiement = models.CharField(max_length=100, blank=True)

    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default=STATUT_RECUE)'''

if "STATUT_PAIEMENT_NON_REQUIS" in contenu:
    print("DEJA FAIT : champs deja presents.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champs de paiement ajoutes a DemandeService.")
else:
    print("ERREUR : ancre introuvable.")