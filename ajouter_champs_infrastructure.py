CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    nom = models.CharField(max_length=200)
    quartier = models.CharField(max_length=150, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='FONCTIONNEL')'''

nouveau = '''    nom = models.CharField(max_length=200)
    quartier = models.CharField(max_length=150, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='FONCTIONNEL')
    sous_type = models.CharField(
        max_length=150, blank=True,
        help_text="Sous-categorie precise (ex: Pharmacie, Poste de sante, Centre de sante...).",
    )
    details = models.JSONField(
        default=dict, blank=True,
        help_text="Attributs specifiques au type d'infrastructure (horaires, telephone, "
                   "nombre d'employes, services, etc.), sous forme libelle -> valeur.",
    )'''

if "sous_type = models.CharField" in contenu:
    print("DEJA FAIT : champs deja presents.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champs sous_type et details ajoutes au modele Infrastructure.")
else:
    print("ERREUR : bloc exact introuvable.")