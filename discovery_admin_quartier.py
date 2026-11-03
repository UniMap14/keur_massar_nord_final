# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Mentions 'statsParQuartier' / 'parcellesParZone' / 'numero_titre_foncier' / 'occupation_sol' ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"statsParQuartier|parcellesParZone|numero_titre_foncier|occupation_sol", l):
        print(f"{i}: {l.strip()}")

print()
print("=== Panneau HTML 'Statistiques par quartier' (recherche du bloc) ===")
for i, l in enumerate(lignes, 1):
    if "Statistiques par quartier" in l or "quartier-select" in l or "quartier-fiche" in l:
        print(f"{i}: {l.strip()}")