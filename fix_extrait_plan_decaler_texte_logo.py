# -*- coding: utf-8 -*-
"""
Le logo agrandi chevauche maintenant "Centre des Services Fiscaux de
Keur Massar" / "Bureau du Cadastre" -- on descend ces deux lignes sous
le logo, et on ajuste le decalage global qui suit pour ne pas chevaucher
la suite de l'en-tete.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_decaler_texte_logo.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

PATCHES = []

PATCHES.append((
    "descendre les 2 lignes sous le logo",
    '    c.setFillColor(GRIS)\n'
    '    c.drawString(marge, y - 19.5 * mm, "Centre des Services Fiscaux de Keur Massar")\n'
    '    c.drawString(marge, y - 23.5 * mm, "Bureau du Cadastre")\n',
    '    c.setFillColor(GRIS)\n'
    '    c.drawString(marge, y - 24 * mm, "Centre des Services Fiscaux de Keur Massar")\n'
    '    c.drawString(marge, y - 28 * mm, "Bureau du Cadastre")\n',
))

PATCHES.append((
    "decalage global apres l'en-tete, agrandi d'autant",
    "    y -= 29.5 * mm\n",
    "    y -= 34 * mm\n",
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
print("OK : texte descendu sous le logo, plus de chevauchement.")