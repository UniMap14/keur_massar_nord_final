# -*- coding: utf-8 -*-
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== Fichiers .html contenant 'geoportail' dans leur nom ou chemin ===")
for racine, dossiers, fichiers in os.walk("foncier/templates"):
    for f in fichiers:
        if "geoportail" in f.lower() or "geoportail" in racine.lower():
            print(os.path.join(racine, f))

print()
print("=== urls.py : routes contenant 'geoportail' ou 'carte' ===")
for chemin_fichier in ["foncier/urls.py", "foncier/dashboard_urls.py", "kmsn/urls.py"]:
    if os.path.exists(chemin_fichier):
        with io.open(chemin_fichier, "r", encoding="utf-8") as f:
            lignes = f.readlines()
        for i, l in enumerate(lignes, 1):
            if re.search(r"geoportail|carte", l, re.IGNORECASE):
                print(f"{chemin_fichier}:{i}: {l.strip()}")

print()
print("=== views.py / dashboard_views.py : fonctions contenant 'geoportail' ou 'carte' ===")
for chemin_fichier in ["foncier/views.py", "foncier/dashboard_views.py"]:
    if os.path.exists(chemin_fichier):
        with io.open(chemin_fichier, "r", encoding="utf-8") as f:
            lignes = f.readlines()
        for i, l in enumerate(lignes, 1):
            if re.search(r"def .*(geoportail|carte)", l, re.IGNORECASE):
                print(f"{chemin_fichier}:{i}: {l.strip()}")