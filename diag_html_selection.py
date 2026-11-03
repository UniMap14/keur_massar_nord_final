# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

for i, l in enumerate(lignes):
    if 'id="selOccupation"' in l:
        debut = i
        fin = min(len(lignes), i + 10)
        print(f"=== Bloc autour de 'selOccupation' (trouve ligne {i+1}) ===")
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes[j])}")
        break