# -*- coding: utf-8 -*-
"""
Script de recherche simple (pas besoin de Django) :
    python audit_simulateur_1_recherche.py

A lancer depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn

Cherche toutes les occurrences de "simulateur" dans le code (vues,
urls, templates) pour localiser la fonctionnalite actuelle.
"""
import os

RACINE = "."
EXTENSIONS = (".py", ".html")
MOTIF = "simulateur"

trouvailles = []
for dossier, _, fichiers in os.walk(RACINE):
    if any(p in dossier for p in (".git", "venv", "__pycache__", "node_modules", "staticfiles")):
        continue
    for nom in fichiers:
        if not nom.endswith(EXTENSIONS):
            continue
        chemin = os.path.join(dossier, nom)
        try:
            with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                lignes = f.readlines()
        except Exception:
            continue
        for i, ligne in enumerate(lignes, start=1):
            if MOTIF in ligne.lower():
                trouvailles.append((chemin, i, ligne.strip()))

print(f"{len(trouvailles)} occurrence(s) de 'simulateur' trouvee(s) :\n")
for chemin, i, ligne in trouvailles:
    print(f"{chemin}:{i}: {ligne}")