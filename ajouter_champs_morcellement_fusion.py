CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    # --- SECTION GÉOGRAPHIQUE (POSTGIS) ---
    geom = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return f"Parcelle {self.nicad} - {self.adresse_parcelle}"'''

nouveau = '''    # --- SECTION GÉOGRAPHIQUE (POSTGIS) ---
    geom = models.MultiPolygonField(srid=4326)

    # --- MORCELLEMENT / FUSION ---
    parcelle_active = models.BooleanField(
        default=True, verbose_name="Parcelle active",
        help_text="Décoché automatiquement si cette parcelle a été fusionnée ou morcelée (remplacée par une ou plusieurs nouvelles parcelles).",
    )
    demande_origine = models.ForeignKey(
        'DemandeMorcellementFusion', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='parcelles_resultantes',
        help_text="Demande de morcellement/fusion à l'origine de cette parcelle, le cas échéant.",
    )

    def __str__(self):
        return f"Parcelle {self.nicad} - {self.adresse_parcelle}"'''

if "parcelle_active" in contenu:
    print("DEJA FAIT : champs deja presents.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champs parcelle_active + demande_origine ajoutes a Parcelle.")
else:
    print("ERREUR : ancre introuvable.")