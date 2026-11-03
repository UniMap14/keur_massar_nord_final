# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
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

imprimer_fonction("mettreAJourRayon")

print("=== HTML panneau rayon (recherche 'rayon-infra-select') ===")
for i, l in enumerate(lignes, 1):
    if "rayon-infra-select" in l or "Centrer sur une infrastructure" in l:
        print(f"{i}: {repr(l)}")

print()
print("=== Variables globales 'modeChoixDestination' / 'modeDessinActif' / selection spatiale presentes ? ===")
for motif in ["modeChoixDestination", "btnChoisirDestination", "calculerSelection", "formeSelectionActuelle", "coucheFormeSelection"]:
    print(motif, ":", motif in "".join(lignes))

print()
print("=== map.on('click' (contexte complet) ===")
debut2 = None
for i, l in enumerate(lignes):
    if "map.on('click', function (e) {" in l:
        debut2 = i
        break
if debut2 is not None:
    for i in range(debut2, min(debut2 + 20, len(lignes))):
        print(repr(lignes[i]))