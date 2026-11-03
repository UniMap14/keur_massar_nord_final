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
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^def |^@", lignes[j]):
            fin = j
            break
    print(f"=== views.py : statistiques(), lignes {debut+1}-{fin} (repr) ===")
    for i in range(debut, fin):
        print(f"{i+1}: {lignes[i]!r}")

print()
print("=== statistiques.html (repr, ligne par ligne) ===")
with io.open("foncier/templates/foncier/statistiques.html", "r", encoding="utf-8") as f:
    lignes_html = f.readlines()
for i, l in enumerate(lignes_html):
    print(f"{i+1}: {l!r}")