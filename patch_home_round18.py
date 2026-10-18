# -*- coding: utf-8 -*-
"""
Round 18 (home.html) : permute l'ordre d'affichage des lignes 2 et 3
de la grille de contenu. Nouvelle ligne 2 : Derniers paiements /
Parcelles en retard / Taux de recouvrement par zone. Nouvelle ligne 3 :
Que voulez-vous faire / Dernieres demandes / Parcelle recente /
Activite recente. Rien n'est deplace dans le HTML, seul l'ordre CSS
("order") change.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE = """    .dashboard-grid .cell-quick-actions   { grid-column: span 2 !important; order: 6  !important; }
    .dashboard-grid .cell-demandes        { grid-column: span 2 !important; order: 7  !important; }
    .dashboard-grid .cell-parcelle-recente{ grid-column: span 1 !important; order: 8  !important; }
    .dashboard-grid .cell-activite        { grid-column: span 1 !important; order: 9  !important; }
    .dashboard-grid .cell-paiements       { grid-column: span 2 !important; order: 10 !important; }
    .dashboard-grid .cell-retardataires   { grid-column: span 2 !important; order: 11 !important; }
    .dashboard-grid .cell-zones           { grid-column: span 2 !important; order: 12 !important; }"""
AJOUT = """    .dashboard-grid .cell-paiements       { grid-column: span 2 !important; order: 6  !important; }
    .dashboard-grid .cell-retardataires   { grid-column: span 2 !important; order: 7  !important; }
    .dashboard-grid .cell-zones           { grid-column: span 2 !important; order: 8  !important; }
    .dashboard-grid .cell-quick-actions   { grid-column: span 2 !important; order: 9  !important; }
    .dashboard-grid .cell-demandes        { grid-column: span 2 !important; order: 10 !important; }
    .dashboard-grid .cell-parcelle-recente{ grid-column: span 1 !important; order: 11 !important; }
    .dashboard-grid .cell-activite        { grid-column: span 1 !important; order: 12 !important; }"""
if "order: 6  !important; }\n    .dashboard-grid .cell-retardataires" in texte:
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
    print("OK : dashboard/home.html -- round 18 (ordre des lignes 2 et 3 permute).")