# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

def bloc(centre, avant, apres, titre):
    debut = max(0, centre - 1 - avant)
    fin = min(len(lignes), centre - 1 + apres)
    print(f"=== {titre} (autour de la ligne {centre}) ===")
    for i in range(debut, fin):
        print(f"{i+1}: {lignes[i]}", end="")
    print()
    print()

# Le bouton "itineraire" qui appelle calculerItineraire(centre.lat, centre.lng) a la ligne 972
bloc(972, 25, 10, "Appel calculerItineraire(centre.lat, centre.lng) ligne 972")

# Le gestionnaire de clic carte generique a la ligne 1751
bloc(1751, 5, 40, "map.on('click', ...) ligne 1751")

# Le panneau HTML route-info (ligne 598) avec un peu plus de contexte avant/apres
bloc(598, 20, 40, "Panneau HTML route-info ligne 598")

# Variables globales liees a l'itineraire : coucheItineraire, userLatLng
print("=== Declarations de 'coucheItineraire' et 'userLatLng' ===")
import re
for i, l in enumerate(lignes, 1):
    if re.search(r"let coucheItineraire|let userLatLng|var coucheItineraire|var userLatLng", l):
        print(f"{i}: {l.strip()}")