# -*- coding: utf-8 -*-
"""
Round 10 (home.html) : separe la grille KPI (reste 6 colonnes, 115px --
deja conforme a la maquette) de la grille des panneaux de contenu, qui
passe a une largeur minimale plus confortable (260px) pour que les
titres de panneaux et les graphiques ne soient plus coupes/ecrases
(Evolution des paiements, Repartition par type, Carte de la commune,
Taux de recouvrement).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Separation des deux grilles + largeur/hauteur des panneaux
# ---------------------------------------------------------------------
ANCRE_GRILLE = """    .kpi-grid,
    .dashboard-grid {
        grid-template-columns: repeat(6, 1fr) !important;
        grid-auto-rows: 115px !important;
        align-items: stretch !important;
        gap: 8px !important;
    }
    .kpi-grid .kpi-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 115px !important;
        overflow: hidden !important;
    }
    .dashboard-grid .panel,
    .dashboard-grid .geo-access-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 115px !important;
        overflow: hidden !important;
        margin: 0 !important;
    }"""
AJOUT_GRILLE = """    .kpi-grid {
        grid-template-columns: repeat(6, 1fr) !important;
        grid-auto-rows: 115px !important;
        align-items: stretch !important;
        gap: 8px !important;
    }
    .kpi-grid .kpi-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 115px !important;
        overflow: hidden !important;
    }
    .dashboard-grid {
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
if "minmax(260px, 1fr)) !important;" in texte:
    pass
elif ANCRE_GRILLE not in texte:
    erreurs.append("ANCRE_GRILLE introuvable")
else:
    texte = texte.replace(ANCRE_GRILLE, AJOUT_GRILLE, 1)

# ---------------------------------------------------------------------
# 2) Plus de hauteur pour les graphiques / mini-carte (ils avaient ete
#    ecrases pour tenir dans des tuiles de 115px, inutile maintenant
#    qu'elles font 190px)
# ---------------------------------------------------------------------
ANCRE_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 62px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 45px !important; }
    .dashboard-grid .mini-map-stats { padding: 2px 6px !important; }"""
AJOUT_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 120px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 95px !important; }
    .dashboard-grid .mini-map-stats { padding: 4px 6px !important; }"""
if "height: 120px !important;" in texte:
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
    print("OK : dashboard/home.html -- round 10 (panneaux de contenu plus larges, titres/graphiques plus lisibles).")