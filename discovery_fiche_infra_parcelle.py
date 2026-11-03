# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("Nombre total de lignes du fichier :", len(lignes))
print()

print("=== Mentions 'ficheHTML', 'fiche-parcelle', 'fiche-infra', 'ficheInfrastructure', 'popupInfra' ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"ficheHTML|fiche-parcelle|fiche-infra|ficheInfrastructure|popupInfra|marqueurInfra|infraMarker", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")

print()
print("=== Mentions 'bindPopup' (contenu des popups sur la carte) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"bindPopup", l):
        print(f"{i}: {l.strip()}")

print()
# Fonction qui construit le ficheHTML des parcelles (contexte autour de la ligne 900-950 deja vue)
print("=== Contexte lignes 895-950 (construction fiche parcelle + distance ?) ===")
print("".join(lignes[894:950]))