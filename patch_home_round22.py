# -*- coding: utf-8 -*-
"""
Round 22 (home.html) : renomme le titre du panneau "Repartition par
type de taxe" en "Infrastructures et parcelles", pour refleter le
nouveau contenu du donut. Regex bornee car l'ancien titre contient
des caracteres accentues.

Idempotent. Ancres 100% ASCII.
"""
import pathlib
import re

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

DEBUT = '<h2><i class="fa-solid fa-chart-pie"></i>'
FIN = '</h2>'
NOUVEAU_TITRE = ' Infrastructures et parcelles'

if "Infrastructures et parcelles</h2>" in texte:
    pass
elif DEBUT not in texte:
    erreurs.append("DEBUT (icone fa-chart-pie) introuvable")
else:
    motif = re.escape(DEBUT) + r".*?" + re.escape(FIN)
    nouveau_texte, nb = re.subn(motif, DEBUT + NOUVEAU_TITRE + FIN, texte, count=1, flags=re.S)
    if nb == 1:
        texte = nouveau_texte
    else:
        erreurs.append("regex titre donut : aucune correspondance")

if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard/home.html -- round 22 (titre du donut mis a jour).")