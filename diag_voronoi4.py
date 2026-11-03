# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi4.py', encoding='utf-8').read())"
"""
chemin = "foncier/templates/foncier/geoportail.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

idx = contenu.find("function analyserZonesSousDesservies")
print("=" * 100)
print("analyserZonesSousDesservies -- SUITE (caracteres 3000 a 6500 apres le debut)")
print("=" * 100)
print(contenu[idx + 3000: idx + 6500])
print()

print("=" * 100)
print("celluleDansLaCommune")
print("=" * 100)
idx2 = contenu.find("function celluleDansLaCommune")
print(contenu[idx2: idx2 + 800] if idx2 != -1 else "introuvable")
print()

print("=" * 100)
print("infrastructuresFiltrees")
print("=" * 100)
idx3 = contenu.find("function infrastructuresFiltrees")
print(contenu[idx3: idx3 + 1200] if idx3 != -1 else "introuvable")