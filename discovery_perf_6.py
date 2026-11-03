# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/views.py"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

for i, l in enumerate(lignes):
    if "CACHE_KEY_PUBLIC = " in l:
        debut = max(0, i - 3)
        fin = min(len(lignes), i + 3)
        print(f"=== Autour de CACHE_KEY_PUBLIC (ligne {i+1}) ===")
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes[j])}")
        break