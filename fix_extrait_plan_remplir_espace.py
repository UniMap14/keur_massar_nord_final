# -*- coding: utf-8 -*-
"""
Ajustements supplementaires sur le plan de l'extrait de plan :
1) Le cadre du plan dans le PDF est agrandi (occupe quasiment toute la
   largeur de la page, au lieu d'une case plus petite au milieu).
2) La marge autour du dessin est encore reduite (moins de blanc perdu
   sur les bords).
3) Un peu plus de parcelles voisines affichees, maintenant que la
   taille du texte s'adapte automatiquement (pas de retour au probleme
   de chiffres qui debordent).

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_remplir_espace.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

PATCHES = []

PATCHES.append((
    "taille du cadre du plan dans le PDF",
    "    taille_plan = min(largeur - 2 * marge, 135 * mm)\n",
    "    taille_plan = min(largeur - 2 * marge, 148 * mm)\n",
))

PATCHES.append((
    "marge autour du dessin (encore plus serree)",
    "    etendue_brute = max(xmax - xmin, ymax - ymin, 10.0)\n"
    "    marge_m = etendue_brute * 0.12 + 4\n",
    "    etendue_brute = max(xmax - xmin, ymax - ymin, 10.0)\n"
    "    marge_m = etendue_brute * 0.06 + 3\n",
))

PATCHES.append((
    "nombre de voisines demande",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=70)\n",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=120)\n",
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
print("OK : plan agrandi dans la page + marge reduite + un peu plus de parcelles.")