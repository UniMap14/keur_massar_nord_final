# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin_pub = "foncier/templates/foncier/geoportail.html"
with io.open(chemin_pub, "r", encoding="utf-8") as f:
    lignes_pub = f.readlines()

def imprimer_fonction(nom_fonction):
    debut = None
    for i, l in enumerate(lignes_pub):
        if re.match(r"\s*function " + re.escape(nom_fonction) + r"\(", l):
            debut = i
            break
    if debut is None:
        print(f"{nom_fonction} INTROUVABLE\n")
        return
    fin = len(lignes_pub)
    niveau = 0
    compte_ouvert = False
    for j in range(debut, len(lignes_pub)):
        niveau += lignes_pub[j].count("{") - lignes_pub[j].count("}")
        if "{" in lignes_pub[j]:
            compte_ouvert = True
        if compte_ouvert and niveau <= 0:
            fin = j + 1
            break
    print(f"=== {nom_fonction}, lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(repr(lignes_pub[i]))
    print()

imprimer_fonction("analyserZonesSousDesservies")
imprimer_fonction("basculerVoronoi")
imprimer_fonction("celluleDansLaCommune")
imprimer_fonction("infrastructuresFiltrees")