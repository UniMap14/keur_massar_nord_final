# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Mentions 'filter-statut' ===")
for i, l in enumerate(lignes, 1):
    if "filter-statut" in l:
        print(f"{i}: {l.strip()}")

print()
print("=== Contexte lignes 1401-1435 (calcul statsParQuartier) ===")
print("".join(lignes[1400:1435]))

print()
print("=== Panneau HTML lignes 415-435 (Statistiques par quartier complet) ===")
print("".join(lignes[414:435]))