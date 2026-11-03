# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("Nombre total de lignes :", len(lignes))
print()
print("=== Lignes 2040 a la fin ===")
print("".join(lignes[2039:]))

print()
print("=== Debut du fichier : imports (lignes 1-40) ===")
print("".join(lignes[0:40]))