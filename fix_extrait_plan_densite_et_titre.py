# -*- coding: utf-8 -*-
"""
Deux ajustements sur l'extrait de plan (foncier/views.py), suite aux
retours sur le rendu :
1) Masquer la ligne "Mt du Titre Foncier .../DP" quand aucun titre
   foncier n'est renseigne pour la parcelle (evite l'affichage
   "Mt du Titre Foncier -/DP").
2) Elargir la recherche des parcelles voisines (rayon et nombre max)
   pour que le plan soit plus dense / rempli, comme sur un vrai extrait
   de plan cadastral (grille serree de petits lots), au lieu de
   quelques parcelles eparpillees avec beaucoup de blanc.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_densite_et_titre.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

PATCHES = []

PATCHES.append((
    "ligne Mt du Titre Foncier conditionnelle",
    '''    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(largeur / 2, y, "PLAN POUR AUTORISATION DE CONSTRUIRE")
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    c.drawCentredString(largeur / 2, y, "Mt du Titre Foncier {}/DP".format(titre_foncier))
    y -= 5 * mm
    libelle_lot = "Lot n° {}".format(parcelle_label)''',
    '''    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(largeur / 2, y, "PLAN POUR AUTORISATION DE CONSTRUIRE")
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    if parcelle.numero_titre_foncier:
        c.drawCentredString(largeur / 2, y, "Mt du Titre Foncier {}/DP".format(titre_foncier))
        y -= 5 * mm
    libelle_lot = "Lot n° {}".format(parcelle_label)''',
))

PATCHES.append((
    "recherche de voisines plus dense",
    "        voisines = _voisines_parcelle(parcelle)\n"
    "        image_plan, echelle_texte = _generer_image_plan_type_officiel(parcelle, voisines)",
    "        voisines = _voisines_parcelle(parcelle, rayon_m=160, max_resultats=160)\n"
    "        image_plan, echelle_texte = _generer_image_plan_type_officiel(parcelle, voisines)",
))

erreurs = []
for nom, ancre, remplacement in PATCHES:
    if ancre not in contenu:
        erreurs.append(f"- ancre introuvable pour « {nom} »")
        continue
    if contenu.count(ancre) != 1:
        erreurs.append(f"- ancre « {nom} » trouvee {contenu.count(ancre)} fois (attendu 1)")
        continue
    contenu = contenu.replace(ancre, remplacement)

if erreurs:
    print("ERREUR : certains blocs n'ont pas pu etre localises tels quels :")
    for e in erreurs:
        print(e)
    raise SystemExit("Aucun fichier n'a ete modifie (securite : tout ou rien).")

with io.open(chemin, "w", encoding="utf-8") as f:
    f.write(contenu)
print("OK : extrait de plan plus dense + titre foncier masque si vide.")