# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()
contenu = "".join(lignes)

print("=== 'calculerItineraire' existe dans admin ? ===")
print("calculerItineraire" in contenu)
print()
print("=== 'route-info' / 'route-pied' / 'position-status' / 'proximite-section' existent ? ===")
for motif in ["route-info", "route-pied", "route-voiture", "route-moto", "route-velo", "position-status", "proximite-section", "btnGeolocaliser", "afficherInfrastructuresProches"]:
    print(motif, ":", motif in contenu)

print()
print("=== Bloc HTML autour de 'position-status' (recherche + contexte) ===")
for i, l in enumerate(lignes, 1):
    if "position-status" in l:
        debut = max(0, i - 5)
        fin = min(len(lignes), i + 40)
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes[j])}")
        break

print()
print("=== map.on('click' actuel (post patch zone tampon) ===")
for i, l in enumerate(lignes, 1):
    if "map.on('click', function (e) {" in l:
        debut = i - 1
        fin = min(len(lignes), debut + 35)
        for j in range(debut, fin):
            print(f"{j+1}: {repr(lignes[j])}")
        break