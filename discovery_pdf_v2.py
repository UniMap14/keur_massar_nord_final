# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== Modele Parcelle complet ===")
with io.open("foncier/models.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()
debut = None
for i, l in enumerate(lignes):
    if re.match(r"^class Parcelle\b", l):
        debut = i
        break
if debut is not None:
    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^class \w", lignes[j]):
            fin = j
            break
    print("".join(lignes[debut:fin]))
else:
    print("INTROUVABLE")

print()
print("=== Librairies installees (pip freeze | matplotlib/gdal/geos/shapely/pillow/gis) ===")
import subprocess
res = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
for ligne in res.stdout.splitlines():
    if re.search(r"matplotlib|gdal|geos|shapely|pillow|gis|django", ligne, re.IGNORECASE):
        print(ligne)

print()
print("=== settings.py : INSTALLED_APPS contient-il django.contrib.gis ? ===")
with io.open("kmsn/settings.py", "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()
print("django.contrib.gis trouve :" , "django.contrib.gis" in contenu)

print()
print("=== Recherche d'un champ geom / MultiPolygon dans tout models.py ===")
with io.open("foncier/models.py", "r", encoding="utf-8") as f:
    for i, l in enumerate(f, 1):
        if re.search(r"geom|MultiPolygon|PointField|PolygonField", l):
            print(f"{i}: {l.rstrip()}")