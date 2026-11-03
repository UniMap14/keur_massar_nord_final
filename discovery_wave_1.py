# -*- coding: utf-8 -*-
import io, re

with io.open("foncier/paiement_gateway.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

debut = None
for i, l in enumerate(lignes):
    if re.search(r"class.*wave", l, re.IGNORECASE) or re.search(r"def .*wave.*\(", l, re.IGNORECASE):
        debut = i
        break

if debut is not None:
    fin = len(lignes)
    niveau_trouve = False
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^class ", lignes[j]):
            fin = j
            break
    print(f"=== Bloc Wave, lignes {debut+1} a {fin} ===")
    for i in range(debut, fin):
        print(f"{i+1}: {lignes[i]!r}")
else:
    print("Aucun bloc 'wave' trouve par la regex.")

print("FIN")