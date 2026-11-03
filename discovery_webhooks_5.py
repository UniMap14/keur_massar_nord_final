# -*- coding: utf-8 -*-
import io

with io.open("foncier/paiement_gateway.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Lignes 1 a 30 (imports) ===")
for i in range(0, 30):
    print(f"{i+1}: {lignes[i]!r}")

print()
print("=== Lignes 110 a 130 (contexte de reverse) ===")
for i in range(109, 130):
    print(f"{i+1}: {lignes[i]!r}")