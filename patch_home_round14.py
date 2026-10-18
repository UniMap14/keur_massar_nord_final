# -*- coding: utf-8 -*-
"""
Round 14 (home.html) : compacte le texte simple restant dans les
panneaux de contenu (message "pas assez de donnees par zone", legende
du donut "Repartition par type") pour qu'il tienne dans la hauteur de
tuile reduite sans avoir besoin de faire defiler a l'interieur.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE = """    .dashboard-grid .empty-state .icon {
        width: 26px !important;
        height: 26px !important;
        font-size: 11px !important;
        margin: 0 auto 6px !important;
    }"""
AJOUT = """    .dashboard-grid .empty-state .icon {
        width: 26px !important;
        height: 26px !important;
        font-size: 11px !important;
        margin: 0 auto 6px !important;
    }

    /* ===== Texte simple + legende compacts dans les tuiles reduites (round 14) ===== */
    .dashboard-grid .panel-body p {
        font-size: 10.5px !important;
        line-height: 1.3 !important;
        margin: 4px 0 0 !important;
    }
    .dashboard-grid .chart-legend-list {
        margin: 4px 0 0 !important;
        gap: 3px !important;
    }
    .dashboard-grid .chart-legend-list li {
        font-size: 10.5px !important;
    }"""
if "Texte simple + legende compacts dans les tuiles reduites (round 14)" in texte:
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
    print("OK : dashboard/home.html -- round 14 (texte/legende compactes).")