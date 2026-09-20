CHEMIN = "citoyens/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    motif_rejet = models.TextField("Motif du rejet", blank=True)

    class Meta:'''

nouveau = '''    motif_rejet = models.TextField("Motif du rejet", blank=True)

    OPERATEURS_PAIEMENT = [
        ("orange_money", "Orange Money"),
        ("wave", "Wave"),
    ]
    operateur_paiement = models.CharField(
        "Opérateur de paiement enregistré", max_length=20,
        choices=OPERATEURS_PAIEMENT, blank=True,
        help_text="Utilisé pour pré-remplir vos paiements de taxation.",
    )

    class Meta:'''

if "operateur_paiement" in contenu:
    print("DEJA FAIT : champ deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champ operateur_paiement ajoute.")
else:
    print("ERREUR : ancre introuvable.")