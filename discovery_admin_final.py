# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== 'echapperHtml' existe ? ===")
for i, l in enumerate(lignes, 1):
    if "echapperHtml" in l and "function" in l:
        print(f"{i}: {l.strip()}")

print()
print("=== Contexte ligne 2448 (onEvent quartier-select, +/- 10 lignes) ===")
for i, l in enumerate(lignes, 1):
    if "onEvent('quartier-select'" in l:
        debut = max(0, i - 3)
        fin = min(len(lignes), i + 5)
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes[j])}")
        break