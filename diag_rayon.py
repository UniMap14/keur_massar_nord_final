# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

debut = None
for i, l in enumerate(lignes):
    if re.match(r"\s*function mettreAJourRayon\(", l):
        debut = i
        break

if debut is None:
    print("mettreAJourRayon INTROUVABLE")
else:
    fin = len(lignes)
    niveau = 0
    compte_ouvert = False
    for j in range(debut, len(lignes)):
        niveau += lignes[j].count("{") - lignes[j].count("}")
        if "{" in lignes[j]:
            compte_ouvert = True
        if compte_ouvert and niveau <= 0:
            fin = j + 1
            break
    print(f"Lignes {debut+1}-{fin} (repr, pour voir les caracteres exacts) :")
    for i in range(debut, fin):
        print(repr(lignes[i]))