# -*- coding: utf-8 -*-
import io, re

with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    contenu = f.read()

print("=== Lignes contenant 'initier_paiement' dans views.py ===")
for i, ligne in enumerate(contenu.splitlines(), start=1):
    if "initier_paiement" in ligne:
        print(f"{i}: {ligne}")

print()
print("=== Contexte autour de chaque appel (10 lignes apres) ===")
lignes = contenu.splitlines()
for i, ligne in enumerate(lignes):
    if "initier_paiement" in ligne:
        for j in range(i, min(len(lignes), i + 12)):
            print(f"{j+1}: {lignes[j]}")
        print("---")

print("FIN")