CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    # Coordonnées facultatives, pour un jour les afficher sur le géoportail
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    notes = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)'''

nouveau = '''    # Coordonnées facultatives, pour un jour les afficher sur le géoportail
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    parcelle = models.ForeignKey(
        Parcelle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="infrastructures",
        help_text="Parcelle qui contient cette infrastructure (déterminée automatiquement par croisement spatial).",
    )

    notes = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)'''

if "parcelle = models.ForeignKey(\n        Parcelle, on_delete=models.SET_NULL, null=True, blank=True,\n        related_name=\"infrastructures\"" in contenu:
    print("DEJA FAIT : champ deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champ parcelle ajoute au modele Infrastructure.")
else:
    print("ERREUR : ancre introuvable.")