# -*- coding: utf-8 -*-
import sys, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== Taille des fichiers templates ===")
for f in ["foncier/templates/foncier/geoportail.html", "foncier/templates/foncier/geoportail_admin.html"]:
    if os.path.exists(f):
        print(f, ":", os.path.getsize(f), "octets")

print()
print("=== Recherche des vues qui fournissent les donnees (zones/parcelles/sections/limites) en JSON/GeoJSON ===")
chemin_views = "foncier/views.py"
if os.path.exists(chemin_views):
    with io.open(chemin_views, "r", encoding="utf-8") as f:
        lignes = f.readlines()
    print(f"Nombre de lignes dans {chemin_views} :", len(lignes))
    for i, l in enumerate(lignes):
        if re.search(r"def (carte_geoportail|.*zones.*json|.*parcelles.*json|.*sections.*json|.*limites.*json|api_|_geojson)", l, re.IGNORECASE):
            print(f"{i+1}: {l.rstrip()}")
else:
    print("foncier/views.py introuvable depuis ce dossier - verifie le chemin.")

print()
print("=== urls.py : routes liees au geoportail ===")
chemin_urls = "foncier/urls.py"
if os.path.exists(chemin_urls):
    with io.open(chemin_urls, "r", encoding="utf-8") as f:
        contenu_urls = f.read()
    for ligne in contenu_urls.splitlines():
        if re.search(r"geoportail|zones|parcelles|sections|limites|infra", ligne, re.IGNORECASE):
            print(ligne)
else:
    print("foncier/urls.py introuvable.")