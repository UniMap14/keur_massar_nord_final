# -*- coding: utf-8 -*-
"""
Elargit le rayon de recherche des parcelles voisines (_voisines_parcelle)
utilise par l'extrait de plan : le rayon minimum et le plafond etaient
trop petits pour afficher autant de parcelles que sur le modele officiel.
Augmente aussi le nombre max de resultats demande par l'extrait de plan.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_plus_de_parcelles.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

PATCHES = []

PATCHES.append((
    "rayon minimum/plafond de _voisines_parcelle",
    "    rayon_m = max(60.0, 0.55 * max(largeur_m, hauteur_m))\n"
    "    rayon_m = min(rayon_m, 350.0)\n",
    "    rayon_m = max(140.0, 0.9 * max(largeur_m, hauteur_m))\n"
    "    rayon_m = min(rayon_m, 650.0)\n",
))

PATCHES.append((
    "appel depuis l'extrait de plan : plus de resultats demandes",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=160)\n",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=320)\n",
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
print("OK : rayon de recherche et nombre de parcelles voisines augmentes.")