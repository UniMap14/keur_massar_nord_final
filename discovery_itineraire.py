# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("Nombre total de lignes du fichier :", len(lignes))
print()

# 1) Fonction calculerItineraire complete
debut = None
for i, l in enumerate(lignes):
    if re.match(r"\s*function calculerItineraire\(", l):
        debut = i
        break

if debut is None:
    print("calculerItineraire INTROUVABLE")
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
    print(f"=== calculerItineraire, lignes {debut+1}-{fin} ===")
    print("".join(lignes[debut:fin]))
    print()

# 2) Fonction afficherInfrastructuresProches complete
debut2 = None
for i, l in enumerate(lignes):
    if re.match(r"\s*function afficherInfrastructuresProches\(", l):
        debut2 = i
        break

if debut2 is None:
    print("afficherInfrastructuresProches INTROUVABLE")
else:
    fin2 = len(lignes)
    niveau = 0
    compte_ouvert = False
    for j in range(debut2, len(lignes)):
        niveau += lignes[j].count("{") - lignes[j].count("}")
        if "{" in lignes[j]:
            compte_ouvert = True
        if compte_ouvert and niveau <= 0:
            fin2 = j + 1
            break
    print(f"=== afficherInfrastructuresProches, lignes {debut2+1}-{fin2} ===")
    print("".join(lignes[debut2:fin2]))
    print()

# 3) Tous les appels a calculerItineraire (pour voir d'ou c'est declenche)
print("=== Tous les appels/references a 'calculerItineraire' ===")
for i, l in enumerate(lignes, 1):
    if "calculerItineraire" in l:
        print(f"{i}: {l.strip()}")

print()
print("=== Tous les 'map.on(' (evenements carte, ex: clic) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"map\.on\(", l):
        print(f"{i}: {l.strip()}")

print()
print("=== Mentions de 'route-info' / 'route-pied' / 'route-voiture' / 'route-velo' (zone d'affichage resultats) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"route-info|route-pied|route-voiture|route-velo|itineraire-panel|destination", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")