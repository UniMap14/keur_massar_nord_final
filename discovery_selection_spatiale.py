# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("Nombre total de lignes du fichier :", len(lignes))
print()

def imprimer_fonction(nom_fonction):
    debut = None
    for i, l in enumerate(lignes):
        if re.match(r"\s*function " + re.escape(nom_fonction) + r"\(", l):
            debut = i
            break
    if debut is None:
        print(f"{nom_fonction} INTROUVABLE (recherche large ci-dessous)")
        for i, l in enumerate(lignes, 1):
            if nom_fonction in l:
                print(f"{i}: {l.strip()}")
        print()
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

# Fonctions liees au dessin / selection spatiale
for nom in ["initialiserDessin", "surFormeDessinee", "lancerSelectionSpatiale", "selectionnerParcellesDansForme", "afficherResultatSelection"]:
    imprimer_fonction(nom)

print("=== Toutes les mentions de 'modeDessinActif', 'draw:created', 'L.Draw', 'selection' (insensible a la casse) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"modeDessinActif|draw:created|L\.Draw|selection", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")

print()
print("=== Boutons/HTML lies au dessin (data-draw, btnDessin, outil de selection) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"dessin|draw-toolbar|outil-selection|spatial", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")