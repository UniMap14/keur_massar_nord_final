# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

motif = re.compile(r"localiser|geolocation|getCurrentPosition", re.IGNORECASE)
indices = [i for i, l in enumerate(lignes) if motif.search(l)]

print("Nombre total de lignes du fichier :", len(lignes))
print("Lignes concernees :", [i+1 for i in indices])
print()

deja_imprime = set()
for idx in indices:
    debut = max(0, idx - 5)
    fin = min(len(lignes), idx + 25)
    print("=" * 70)
    print(f"Autour de la ligne {idx+1}")
    print("=" * 70)
    for i in range(debut, fin):
        if i not in deja_imprime:
            print(f"{i+1}: {lignes[i]}", end="")
            deja_imprime.add(i)
    print()