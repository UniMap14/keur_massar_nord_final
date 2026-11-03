# -*- coding: utf-8 -*-
"""
Zoom un peu plus sur le plan (moins de parcelles voisines affichees,
mais chacune plus grande), et marge encore un peu reduite.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_zoom_plus.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

PATCHES = []

PATCHES.append((
    "nombre de voisines demande (zoom)",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=220)\n",
    "        voisines = _voisines_parcelle(parcelle, max_resultats=110)\n",
))

PATCHES.append((
    "marge encore un peu reduite",
    "    marge_m_x = etendue_brute_x * 0.04 + 2\n"
    "    marge_m_y = etendue_brute_y * 0.04 + 2\n",
    "    marge_m_x = etendue_brute_x * 0.025 + 1\n"
    "    marge_m_y = etendue_brute_y * 0.025 + 1\n",
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
print("OK : zoom accentue (moins de parcelles, chacune plus grande).")