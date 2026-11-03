# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/views.py"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

debut = None
for i, l in enumerate(lignes):
    if re.match(r"def statistiques\(", l):
        debut = i
        break
fin = len(lignes)
if debut is not None:
    for j in range(debut, len(lignes)):
        if j > debut and re.match(r"^def |^@", lignes[j]):
            fin = j
            break
    print(f"=== statistiques(), lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(lignes[i], end="")
print()
print("=== Template statistiques.html (complet) ===")
with io.open("foncier/templates/foncier/statistiques.html", "r", encoding="utf-8") as f:
    print(f.read())