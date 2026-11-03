# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

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
    print(f"=== {nom_fonction}, lignes {debut+1}-{fin} (repr) ===")
    for i in range(debut, fin):
        print(repr(lignes[i]))
    print()

imprimer_fonction("calculerSelection")

print("=== HTML lignes 380-400 (panneau rayon, repr) ===")
for i in range(379, 400):
    print(f"{i+1}: {repr(lignes[i])}")

print()
print("=== Variable 'let modeDessinActif' / globales selection (contexte) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"let modeDessinActif|let coucheRayon|let selectionFeatures|let selectionSet", l):
        print(f"{i}: {l.strip()}")