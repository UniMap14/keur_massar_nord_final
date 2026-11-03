# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

debut = None
for i, l in enumerate(lignes):
    if re.match(r"^def carte_geoportail\(request\):", l):
        debut = i
        break

if debut is None:
    print("Vue carte_geoportail introuvable, recherche large :")
    for i, l in enumerate(lignes, 1):
        if "carte_geoportail" in l:
            print(f"{i}: {l.strip()}")
else:
    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^def \w", lignes[j]):
            fin = j
            break
    print(f"=== carte_geoportail, lignes {debut+1}-{fin} ===")
    print("".join(lignes[debut:fin]))