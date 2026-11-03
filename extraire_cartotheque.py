# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== foncier/views.py lignes 1050-1085 (vue cartotheque) ===")
with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()
print("".join(lignes[1049:1085]))

print()
print("=== foncier/templates/foncier/cartotheque.html (fichier complet) ===")
with io.open("foncier/templates/foncier/cartotheque.html", "r", encoding="utf-8") as f:
    print(f.read())