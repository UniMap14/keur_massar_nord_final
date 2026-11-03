# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi3.py', encoding='utf-8').read())"
"""
chemin = "foncier/templates/foncier/geoportail.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

# Fonction basculerVoronoi (desserte/Voronoi)
idx1 = contenu.find("function basculerVoronoi")
print("=" * 100)
print("basculerVoronoi (a partir de la position", idx1, ")")
print("=" * 100)
print(contenu[idx1:idx1 + 3200])
print()

idx2 = contenu.find("function analyserZonesSousDesservies")
print("=" * 100)
print("analyserZonesSousDesservies (a partir de la position", idx2, ")")
print("=" * 100)
print(contenu[idx2:idx2 + 3200])