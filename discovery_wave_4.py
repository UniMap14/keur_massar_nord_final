# -*- coding: utf-8 -*-
import io

with io.open("citoyens/views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Lignes 220 a 270 ===")
for i in range(219, 270):
    print(f"{i+1}: {lignes[i]!r}")

print()
print("=== Lignes 1075 a 1130 ===")
for i in range(1074, 1130):
    print(f"{i+1}: {lignes[i]!r}")