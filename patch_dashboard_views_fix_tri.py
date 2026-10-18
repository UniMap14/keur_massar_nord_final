# -*- coding: utf-8 -*-
"""
Corrige une TypeError ("can't compare datetime.datetime to datetime.date")
dans le fil d'activite recente de dashboard_home() : certains modeles ont
un champ date (DateField) et d'autres un champ date+heure (DateTimeField),
ce qui empeche de les comparer directement lors du tri.

Fix : on trie sur la representation ISO (.isoformat()) de chaque date, qui
fonctionne de la meme facon pour un date et un datetime, sans rien changer
au contenu affiche.

Idempotent.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE = '    evenements.sort(key=lambda e: e["date"], reverse=True)'
AJOUT = '    evenements.sort(key=lambda e: e["date"].isoformat(), reverse=True)'

if 'e["date"].isoformat()' in texte:
    pass
elif ANCRE not in texte:
    erreurs.append("ANCRE introuvable")
else:
    texte = texte.replace(ANCRE, AJOUT, 1)

if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : foncier/dashboard_views.py corrige (tri du fil d'activite).")