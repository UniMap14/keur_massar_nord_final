# -*- coding: utf-8 -*-
"""
Grille unifiee demandee : 6 colonnes, tuiles toutes egales (meme
largeur, meme hauteur), sur la premiere page.

Methode : les 9 cartes KPI (grille .kpi-grid) + les 9 panneaux de
contenu + le bandeau d'actions (grille .dashboard-grid) sont chacun
forces a 6 colonnes egales -> 9 elements = 2 lignes (6+3) par grille,
soit 4 lignes au total pour les deux grilles empilees. Tous les
placements speciaux ajoutes precedemment (banniere Geoportail en pleine
largeur, ligne zones+taxes groupee, bandeau actions en pleine largeur)
sont neutralises pour que chaque tuile ait exactement la meme taille.

Le wrapper ".stats-charts-row" est rendu invisible au niveau boite
(display: contents) : ses deux panneaux enfants (zones, taxes)
deviennent alors des tuiles normales de la grille, au lieu de former
une mini-grille a part.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

MARQUEUR = "Grille unifiee 6 colonnes"
DEJA_APPLIQUE = MARQUEUR in texte

ANCRE = """    .activity-icon { width: 24px !important; height: 24px !important; }
</style>
{% endblock %}"""
AJOUT = """    .activity-icon { width: 24px !important; height: 24px !important; }

    /* ===== Grille unifiee 6 colonnes, tuiles toutes egales ===== */
    .kpi-grid,
    .dashboard-grid {
        grid-template-columns: repeat(6, 1fr) !important;
        grid-auto-rows: 160px !important;
        align-items: stretch !important;
        gap: 10px !important;
    }
    .kpi-grid .kpi-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 160px !important;
        overflow: hidden !important;
    }
    .dashboard-grid .panel,
    .dashboard-grid .geo-access-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 160px !important;
        overflow: hidden !important;
        margin: 0 !important;
    }
    /* La ligne zones+taxes redevient deux tuiles normales de la grille */
    .stats-charts-row { display: contents !important; }
    .dashboard-grid .panel-body {
        overflow: hidden !important;
    }
    .dashboard-grid .panel-body.flush {
        max-height: none !important;
        height: 100% !important;
        overflow-y: auto !important;
    }
    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 95px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 80px !important; }
    .dashboard-grid .mini-map-stats { padding: 4px 6px !important; }
    .dashboard-grid .mini-map-stats .mm-value { font-size: 13px !important; }
    .dashboard-grid .mini-map-stats .mm-label { font-size: 8.5px !important; }
    /* Le bandeau "Que voulez-vous faire ?" devient une tuile normale : le
       texte d'intro et les 4 actions se compressent dans la meme tuile */
    .dashboard-grid .quick-actions-banner { padding: 6px 10px !important; }
    .dashboard-grid .quick-actions-banner-text .eyebrow { display: none !important; }
    .dashboard-grid .quick-actions-banner-text .title { font-size: 11px !important; }
    .dashboard-grid .quick-actions-grid {
        grid-template-columns: repeat(4, 1fr) !important;
        height: calc(100% - 26px) !important;
    }
    .dashboard-grid .quick-action-tile { padding: 4px 6px !important; gap: 4px !important; }
    .dashboard-grid .quick-action-icon { width: 22px !important; height: 22px !important; font-size: 10px !important; }
    .dashboard-grid .quick-action-tile span { font-size: 9px !important; line-height: 1.2 !important; }
</style>
{% endblock %}"""

if DEJA_APPLIQUE:
    pass
elif ANCRE not in texte:
    erreurs.append("ANCRE introuvable")
else:
    texte = texte.replace(ANCRE, AJOUT, 1)

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
    print("OK : dashboard/home.html -- grille unifiee 6 colonnes / tuiles egales.")