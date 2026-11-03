# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

for i, l in enumerate(lignes):
    if "btnGeolocaliser" in l and "id=" in l:
        debut = max(0, i - 2)
        fin = min(len(lignes), i + 6)
        print(f"=== Bloc autour de 'btnGeolocaliser' (trouve ligne {i+1}) ===")
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes[j])}")
        print()