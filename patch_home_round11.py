# -*- coding: utf-8 -*-
"""
Round 11 (home.html) : revient a 6 colonnes pour la grille de contenu
(comme pour les KPI), afin que tout retienne sur un seul ecran sans
defilement, mais avec une hauteur de tuile un peu plus genereuse
(150px au lieu de 115px) et des graphiques un peu plus hauts (92px au
lieu de 62px) pour eviter que les titres/graphiques soient de nouveau
ecrases comme avant le round 10.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Dashboard-grid : retour a 6 colonnes, hauteur 150px
# ---------------------------------------------------------------------
ANCRE_GRILLE = """    .dashboard-grid {
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)) !important;
        grid-auto-rows: 190px !important;
        align-items: stretch !important;
        gap: 8px !important;
    }
    .dashboard-grid .panel,
    .dashboard-grid .geo-access-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 190px !important;
        overflow: hidden !important;
        margin: 0 !important;
    }"""
AJOUT_GRILLE = """    .dashboard-grid {
        grid-template-columns: repeat(6, 1fr) !important;
        grid-auto-rows: 150px !important;
        align-items: stretch !important;
        gap: 8px !important;
    }
    .dashboard-grid .panel,
    .dashboard-grid .geo-access-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 150px !important;
        overflow: hidden !important;
        margin: 0 !important;
    }"""
if "grid-auto-rows: 150px !important;" in texte:
    pass
elif ANCRE_GRILLE not in texte:
    erreurs.append("ANCRE_GRILLE introuvable")
else:
    texte = texte.replace(ANCRE_GRILLE, AJOUT_GRILLE, 1)

# ---------------------------------------------------------------------
# 2) Graphiques / mini-carte : hauteur intermediaire (ni 62px ni 120px)
# ---------------------------------------------------------------------
ANCRE_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 120px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 95px !important; }
    .dashboard-grid .mini-map-stats { padding: 4px 6px !important; }"""
AJOUT_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 92px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 68px !important; }
    .dashboard-grid .mini-map-stats { padding: 3px 6px !important; }"""
if "height: 92px !important;" in texte:
    pass
elif ANCRE_CHARTS not in texte:
    erreurs.append("ANCRE_CHARTS introuvable")
else:
    texte = texte.replace(ANCRE_CHARTS, AJOUT_CHARTS, 1)

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
    print("OK : dashboard/home.html -- round 11 (6 colonnes + hauteur intermediaire, tient sur un ecran).")