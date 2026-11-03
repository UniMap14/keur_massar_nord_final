# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== generic_list_stub.html lignes 1-30 ===")
with io.open("foncier/templates/dashboard/generic_list_stub.html", "r", encoding="utf-8") as f:
    lignes = f.readlines()
print("".join(lignes[:30]))

print()
print("=== recherche_cadastrale.html (foncier/) lignes 1-70, pour le style des cartes de resultat ===")
with io.open("foncier/templates/foncier/recherche_cadastrale.html", "r", encoding="utf-8") as f:
    lignes2 = f.readlines()
print("".join(lignes2[:70]))