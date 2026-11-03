# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== 'turf' (librairie geometrie) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"turf", l, re.IGNORECASE):
        print(f"{i}: {l.rstrip()}")

print()
print("=== Chargement des zones (fetch/api zones, variable zones) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"api[_-]?zones|allZones|zonesLayer|zonesGeojson|/zones/", l, re.IGNORECASE):
        print(f"{i}: {l.rstrip()}")

print()
print("=== <script src= (librairies externes chargees) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"<script\s+src=", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")

print()
print("=== user.is_authenticated / citoyen dans le template (lien utilisateur-parcelle) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"is_authenticated|request\.user|citoyen", l, re.IGNORECASE):
        print(f"{i}: {l.strip()}")