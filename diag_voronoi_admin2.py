# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi_admin2.py', encoding='utf-8').read())"
"""
chemin = "foncier/templates/foncier/geoportail_admin.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    lignes = f.readlines()

def imprimer_plage(etiquette, debut, fin):
    print("=" * 100)
    print(etiquette, f"(lignes {debut+1} a {fin})")
    print("=" * 100)
    for i in range(max(0,debut), min(len(lignes), fin)):
        print(repr(lignes[i]))
    print()

idx_analyser = next((i for i, l in enumerate(lignes) if "function analyserZonesSousDesservies" in l), None)
idx_baseParcelles = next((i for i, l in enumerate(lignes) if "const baseParcelles" in l), None)

if idx_analyser is not None:
    imprimer_plage("Avant analyserZonesSousDesservies", idx_analyser - 5, idx_analyser + 1)
else:
    print("fonction analyserZonesSousDesservies introuvable !")

if idx_baseParcelles is not None:
    imprimer_plage("Boucle parcelles (depuis 'const baseParcelles')", idx_baseParcelles, idx_baseParcelles + 13)
else:
    print("'const baseParcelles' introuvable !")