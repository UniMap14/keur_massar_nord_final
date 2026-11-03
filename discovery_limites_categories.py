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

imprimer_fonction("loadLimites")

print("=== Toutes les mentions de 'allLimites' / 'Limites' (variable globale) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"allLimites|limites\s*=|coucheLimites", l):
        print(f"{i}: {l.strip()}")

print()
print("=== Select 'filter-infra-categorie' : options HTML + JS de remplissage ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"filter-infra-categorie|infra-categorie", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")

print()
print("=== Mentions 'categorie' sur les objets infra (proprietes disponibles) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"\.categorie\b", l):
        print(f"{i}: {l.strip()}")