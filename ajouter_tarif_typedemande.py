CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    necessite_parcelle = models.BooleanField(
        default=False,
        help_text="Cocher si cette démarche concerne une parcelle précise (ex : extrait cadastral)."
    )
    actif = models.BooleanField(default=True)'''

nouveau = '''    necessite_parcelle = models.BooleanField(
        default=False,
        help_text="Cocher si cette démarche concerne une parcelle précise (ex : extrait cadastral)."
    )
    tarif = models.DecimalField(
        max_digits=10, decimal_places=0, default=0,
        verbose_name="Tarif (FCFA)",
        help_text="0 = démarche gratuite. Si > 0, le paiement est exigé avant délivrance du document.",
    )
    actif = models.BooleanField(default=True)'''

if "tarif = models.DecimalField" in contenu:
    print("DEJA FAIT : champ deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champ tarif ajoute a TypeDemande.")
else:
    print("ERREUR : ancre introuvable.")