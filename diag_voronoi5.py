# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi5.py', encoding='utf-8').read())"

Objectif : recuperer les lignes exactes (avec leur indentation precise,
ligne par ligne, sans ambiguite) des deux boucles a optimiser, et de
l'endroit ou inserer les fonctions utilitaires.
"""
chemin = "foncier/templates/foncier/geoportail.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    lignes = f.readlines()

def imprimer_plage(etiquette, debut, fin):
    print("=" * 100)
    print(etiquette, f"(lignes {debut+1} a {fin})")
    print("=" * 100)
    for i in range(debut, fin):
        print(repr(lignes[i]))
    print()

# Localiser les lignes cles par recherche exacte
idx_celluleDans = next(i for i, l in enumerate(lignes) if "function celluleDansLaCommune" in l)
idx_analyser = next(i for i, l in enumerate(lignes) if "function analyserZonesSousDesservies" in l)
idx_pas = next(i for i, l in enumerate(lignes) if "const pas = 0.0018" in l)
idx_baseParcelles = next(i for i, l in enumerate(lignes) if "const baseParcelles" in l)

imprimer_plage("Avant analyserZonesSousDesservies (pour reperer ou inserer les helpers)", idx_analyser - 3, idx_analyser + 1)
imprimer_plage("Boucle grille (depuis 'const pas')", idx_pas, idx_pas + 16)
imprimer_plage("Boucle parcelles (depuis 'const baseParcelles')", idx_baseParcelles, idx_baseParcelles + 11)