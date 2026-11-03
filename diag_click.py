# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

debut = None
for i, l in enumerate(lignes):
    if "map.on('click', function (e) {" in l:
        debut = i
        break

if debut is None:
    print("ANCRE INTROUVABLE")
else:
    fin = debut + 30
    print(f"Lignes {debut+1}-{fin} (repr) :")
    for i in range(debut, min(fin, len(lignes))):
        print(repr(lignes[i]))