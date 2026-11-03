# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/views.py"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

def imprimer(debut_ligne, fin_ligne, titre):
    print(f"=== {titre} (lignes {debut_ligne}-{fin_ligne}) ===")
    for i in range(debut_ligne - 1, min(fin_ligne, len(lignes))):
        print(f"{i+1}: {lignes[i]}", end="")
    print()

imprimer(322, 420, "api_parcelles_geojson + api_parcelles_toutes_geojson")
imprimer(458, 560, "api_parcelles_geojson_admin + api_parcelles_toutes_geojson_admin")
imprimer(793, 845, "api_zones_geojson + api_sections_geojson + api_limites_geojson")
imprimer(176, 230, "carte_geoportail + carte_geoportail_admin")