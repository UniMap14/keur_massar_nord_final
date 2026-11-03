# -*- coding: utf-8 -*-
"""
Corrige l'appel a _voisines_parcelle dans extrait_cadastral_pdf_view :
cette fonction n'a pas (plus) de parametre 'rayon_m' (elle calcule son
propre rayon adaptatif en interne, plafonne a 350m) -- seul
'max_resultats' existe.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_appel_voisines.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

ancre = "        voisines = _voisines_parcelle(parcelle, rayon_m=160, max_resultats=160)\n"
remplacement = "        voisines = _voisines_parcelle(parcelle, max_resultats=160)\n"

if remplacement in contenu and ancre not in contenu:
    print("Deja applique, rien a faire.")
elif ancre not in contenu:
    raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")
else:
    if contenu.count(ancre) != 1:
        raise SystemExit("ANCRE trouvee plusieurs fois - abandon par securite.")
    contenu = contenu.replace(ancre, remplacement)
    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : appel a _voisines_parcelle corrige (max_resultats=160, sans rayon_m).")