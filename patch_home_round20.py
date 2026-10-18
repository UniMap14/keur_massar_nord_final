# -*- coding: utf-8 -*-
"""
Round 20 (home.html) : regroupe les 4 panneaux de contenu restants
(Derniers paiements, Parcelles en retard, Que voulez-vous faire,
Activite recente) sur UNE SEULE ligne de 6 colonnes au lieu de deux
lignes trop larges. Paiements et Retardataires gardent 2 colonnes
(tableaux, ont besoin de largeur) ; Que voulez-vous faire et Activite
recente passent a 1 colonne chacun (2+2+1+1=6). Le bandeau d'actions
rapides passe de 4 icones en ligne a une grille 2x2 pour rester
lisible dans sa colonne plus etroite.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Largeurs/ordre : les 4 panneaux sur une seule ligne
# ---------------------------------------------------------------------
ANCRE_ORG = """    .dashboard-grid .cell-paiements       { grid-column: span 3 !important; order: 6 !important; }
    .dashboard-grid .cell-retardataires   { grid-column: span 3 !important; order: 7 !important; }
    .dashboard-grid .cell-quick-actions   { grid-column: span 3 !important; order: 8 !important; }
    .dashboard-grid .cell-activite        { grid-column: span 3 !important; order: 9 !important; }"""
AJOUT_ORG = """    .dashboard-grid .cell-paiements       { grid-column: span 2 !important; order: 6 !important; }
    .dashboard-grid .cell-retardataires   { grid-column: span 2 !important; order: 7 !important; }
    .dashboard-grid .cell-quick-actions   { grid-column: span 1 !important; order: 8 !important; }
    .dashboard-grid .cell-activite        { grid-column: span 1 !important; order: 9 !important; }"""
if "order: 8 !important; }\n    .dashboard-grid .cell-activite        { grid-column: span 1" in texte:
    pass
elif ANCRE_ORG not in texte:
    erreurs.append("ANCRE_ORG introuvable")
else:
    texte = texte.replace(ANCRE_ORG, AJOUT_ORG, 1)

# ---------------------------------------------------------------------
# 2) Bandeau d'actions rapides : 2x2 au lieu de 4 en ligne (colonne
#    plus etroite maintenant)
# ---------------------------------------------------------------------
ANCRE_QA = """    .dashboard-grid .quick-actions-grid {
        grid-template-columns: repeat(4, 1fr) !important;
        height: calc(100% - 26px) !important;
    }"""
AJOUT_QA = """    .dashboard-grid .quick-actions-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        height: calc(100% - 26px) !important;
    }"""
if "grid-template-columns: repeat(2, 1fr) !important;\n        height: calc(100% - 26px)" in texte:
    pass
elif ANCRE_QA not in texte:
    erreurs.append("ANCRE_QA introuvable")
else:
    texte = texte.replace(ANCRE_QA, AJOUT_QA, 1)

# ---------------------------------------------------------------------
if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard/home.html -- round 20 (4 panneaux regroupes sur une seule ligne).")