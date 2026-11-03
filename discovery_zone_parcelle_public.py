# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

def imprimer_fonction(nom_fonction):
    debut = None
    for i, l in enumerate(lignes):
        if re.match(r"\s*function " + re.escape(nom_fonction) + r"\(", l):
            debut = i
            break
    if debut is None:
        print(f"{nom_fonction} INTROUVABLE\n")
        return
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
    print(f"=== {nom_fonction}, lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(repr(lignes[i]))
    print()

imprimer_fonction("afficherZoneEtParcelle")

print("=== appel de afficherZoneEtParcelle (contexte) ===")
for i, l in enumerate(lignes):
    if "afficherZoneEtParcelle(" in l and "function" not in l:
        debut = max(0, i - 5)
        fin = min(len(lignes), i + 3)
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes[j])}")
        print()