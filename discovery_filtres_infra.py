# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("Nombre total de lignes du fichier :", len(lignes))
print()

print("=== Toutes les mentions de 'filteredParcelles' ===")
for i, l in enumerate(lignes, 1):
    if "filteredParcelles" in l:
        print(f"{i}: {l.strip()}")

print()
print("=== Fonction qui applique les filtres (recherche la fonction contenant 'filter-occupation' ou 'appliquerFiltres') ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"appliquerFiltres|function.*[Ff]iltre|filter-occupation|search-nicad", l):
        print(f"{i}: {l.strip()}")

print()
# toutesLesInfrastructures function
debut = None
for i, l in enumerate(lignes):
    if re.match(r"\s*function toutesLesInfrastructures\(", l):
        debut = i
        break
if debut is None:
    print("toutesLesInfrastructures INTROUVABLE")
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
    print(f"=== toutesLesInfrastructures, lignes {debut+1}-{fin} ===")
    print("".join(lignes[debut:fin]))

print()
print("=== Mentions 'infraSansParcelle', 'allParcelles =' (chargement) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"infraSansParcelle|allParcelles\s*=", l):
        print(f"{i}: {l.strip()}")