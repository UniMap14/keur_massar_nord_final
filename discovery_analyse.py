# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("Nombre total de lignes du fichier :", len(lignes))
print()

print("=== Mentions 'sous-desservies' / 'sousDesservi' / 'Voronoi' / 'voronoi' / 'desserte' ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"sous.?dessert|voronoi|desserte", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")

print()
print("=== Onglet 'Analyse' (data-tab, id analyse, panneau HTML) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"[Aa]nalyse", l):
        print(f"{i}: {l.strip()}")