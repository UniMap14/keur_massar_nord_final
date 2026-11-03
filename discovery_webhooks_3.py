# -*- coding: utf-8 -*-
import io

with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Lignes 1370 a 1430 (avec numeros) ===")
for i in range(1369, 1430):
    print(f"{i+1}: {lignes[i]!r}")