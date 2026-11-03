# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Toutes les mentions 'rayon-infra-select' / 'rayon-slider' / 'rayon-result' / 'rayon-value' ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"rayon-infra-select|rayon-slider|rayon-result|rayon-value", l):
        print(f"{i}: {l.strip()}")

def imprimer_fonction(nom_fonction):
    debut = None
    for i, l in enumerate(lignes):
        if re.match(r"\s*function " + re.escape(nom_fonction) + r"\(", l):
            debut = i
            break
    if debut is None:
        print(f"{nom_fonction} INTROUVABLE")
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
    print("".join(lignes[debut:fin]))
    print()

for nom in ["analyserRayon", "calculerRayon", "majRayon", "afficherRayon"]:
    imprimer_fonction(nom)

print("=== onEvent lies a rayon ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"onEvent\('rayon", l):
        print(f"{i}: {l.strip()}")