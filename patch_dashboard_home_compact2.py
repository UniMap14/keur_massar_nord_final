# -*- coding: utf-8 -*-
"""
Compaction agressive (round 2) du tableau de bord : reduit encore les
icones, graphiques, mini-carte, tuile Geoportail et listes, pour que le
maximum de contenu tienne dans la premiere vue d'ecran. Quitte a etre
plus petit visuellement, l'objectif explicite est de minimiser le
defilement.

Limite assumee : le padding interne de .panel-header / .panel-body et
la hauteur de l'entete/barre laterale de base.html ne sont pas modifies
ici (fichiers non fournis) -- seul ce qui est stylé dans home.html lui
meme est resserre.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

DEJA_APPLIQUE = "margin-bottom   : 8px;" in texte

# ---------------------------------------------------------------------
# 1) Icones des cartes KPI plus petites
# ---------------------------------------------------------------------
ANCRE_KPI_ICON = """    .kpi-card .kpi-icon {
        width           : 40px;
        height          : 40px;
        border-radius   : 11px;
        display         : flex;
        align-items     : center;
        justify-content : center;
        margin-bottom   : 14px;
        font-size       : 16px;
    }"""
AJOUT_KPI_ICON = """    .kpi-card .kpi-icon {
        width           : 32px;
        height          : 32px;
        border-radius   : 9px;
        display         : flex;
        align-items     : center;
        justify-content : center;
        margin-bottom   : 8px;
        font-size       : 14px;
    }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_KPI_ICON not in texte:
    erreurs.append("ANCRE_KPI_ICON introuvable")
else:
    texte = texte.replace(ANCRE_KPI_ICON, AJOUT_KPI_ICON, 1)

# ---------------------------------------------------------------------
# 2) Sparklines des cartes KPI plus petites
# ---------------------------------------------------------------------
ANCRE_SPARK = """    .kpi-sparkline-wrap {
        position: relative;
        width: 100%;
        height: 30px;
        margin-top: 10px;
        z-index: 1;
        overflow: hidden;
    }"""
AJOUT_SPARK = """    .kpi-sparkline-wrap {
        position: relative;
        width: 100%;
        height: 22px;
        margin-top: 6px;
        z-index: 1;
        overflow: hidden;
    }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_SPARK not in texte:
    erreurs.append("ANCRE_SPARK introuvable")
else:
    texte = texte.replace(ANCRE_SPARK, AJOUT_SPARK, 1)

# ---------------------------------------------------------------------
# 3) Tuile Geoportail (bandeau) : icone, padding et textes reduits
# ---------------------------------------------------------------------
ANCRE_GEOCARD = """    .geo-access-card {
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);
        border-radius: 14px;
        padding: 26px 28px;"""
AJOUT_GEOCARD = """    .geo-access-card {
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);
        border-radius: 12px;
        padding: 16px 18px;"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_GEOCARD not in texte:
    erreurs.append("ANCRE_GEOCARD introuvable")
else:
    texte = texte.replace(ANCRE_GEOCARD, AJOUT_GEOCARD, 1)

ANCRE_GEOICON = """    .geo-access-icon {
        width: 52px; height: 52px; border-radius: 14px; flex-shrink: 0;"""
AJOUT_GEOICON = """    .geo-access-icon {
        width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_GEOICON not in texte:
    erreurs.append("ANCRE_GEOICON introuvable")
else:
    texte = texte.replace(ANCRE_GEOICON, AJOUT_GEOICON, 1)

ANCRE_GEOTEXTE = """    .geo-access-text h3 {
        font-size: 16.5px; font-weight: 700; color: #fff; margin: 0 0 4px;
    }
    .geo-access-text p {
        font-size: 12.5px; color: rgba(255,255,255,.7); margin: 0;
    }
    .geo-access-btn {
        position: relative; z-index: 1;
        display: inline-flex; align-items: center; gap: 9px;
        background: linear-gradient(135deg, #e0b854, #c9982e);
        color: #3c2a20; font-weight: 700; font-size: 13.5px;
        padding: 12px 22px; border-radius: 999px; white-space: nowrap;
        transition: box-shadow .2s ease;
    }"""
AJOUT_GEOTEXTE = """    .geo-access-text h3 {
        font-size: 14px; font-weight: 700; color: #fff; margin: 0 0 2px;
    }
    .geo-access-text p {
        font-size: 11px; color: rgba(255,255,255,.7); margin: 0;
    }
    .geo-access-btn {
        position: relative; z-index: 1;
        display: inline-flex; align-items: center; gap: 7px;
        background: linear-gradient(135deg, #e0b854, #c9982e);
        color: #3c2a20; font-weight: 700; font-size: 12px;
        padding: 8px 16px; border-radius: 999px; white-space: nowrap;
        transition: box-shadow .2s ease;
    }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_GEOTEXTE not in texte:
    erreurs.append("ANCRE_GEOTEXTE introuvable")
else:
    texte = texte.replace(ANCRE_GEOTEXTE, AJOUT_GEOTEXTE, 1)

# ---------------------------------------------------------------------
# 4) Graphiques encore moins hauts (round 2)
# ---------------------------------------------------------------------
ANCRE_CHARTS2 = """    .chart-wrap { position: relative; width: 100%; height: 190px; }
    .chart-wrap-sm { height: 150px; }"""
AJOUT_CHARTS2 = """    .chart-wrap { position: relative; width: 100%; height: 140px; }
    .chart-wrap-sm { height: 110px; }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_CHARTS2 not in texte:
    erreurs.append("ANCRE_CHARTS2 introuvable")
else:
    texte = texte.replace(ANCRE_CHARTS2, AJOUT_CHARTS2, 1)

# ---------------------------------------------------------------------
# 5) Grille : espacement encore reduit
# ---------------------------------------------------------------------
ANCRE_GAP2 = """    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        align-items: stretch;
    }"""
AJOUT_GAP2 = """    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        align-items: stretch;
    }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_GAP2 not in texte:
    erreurs.append("ANCRE_GAP2 introuvable")
else:
    texte = texte.replace(ANCRE_GAP2, AJOUT_GAP2, 1)

# ---------------------------------------------------------------------
# 6) Mini-carte encore moins haute
# ---------------------------------------------------------------------
ANCRE_CARTE2 = '    .mini-map-canvas { height: 140px; width: 100%; }'
AJOUT_CARTE2 = '    .mini-map-canvas { height: 110px; width: 100%; }'
if DEJA_APPLIQUE:
    pass
elif ANCRE_CARTE2 not in texte:
    erreurs.append("ANCRE_CARTE2 introuvable")
else:
    texte = texte.replace(ANCRE_CARTE2, AJOUT_CARTE2, 1)

ANCRE_MMSTATS = """    .mini-map-stats {
        display: flex;
        justify-content: space-around;
        padding: 14px 10px;
        border-top: 1px solid var(--border, #eee6d6);
    }"""
AJOUT_MMSTATS = """    .mini-map-stats {
        display: flex;
        justify-content: space-around;
        padding: 8px 8px;
        border-top: 1px solid var(--border, #eee6d6);
    }"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_MMSTATS not in texte:
    erreurs.append("ANCRE_MMSTATS introuvable")
else:
    texte = texte.replace(ANCRE_MMSTATS, AJOUT_MMSTATS, 1)

# ---------------------------------------------------------------------
# 7) Plafond des listes/tableaux reduit (round 2)
# ---------------------------------------------------------------------
ANCRE_FLUSH2 = '    .dashboard-grid .panel-body.flush { max-height: 280px; overflow-y: auto; }'
AJOUT_FLUSH2 = '    .dashboard-grid .panel-body.flush { max-height: 200px; overflow-y: auto; }'
if DEJA_APPLIQUE:
    pass
elif ANCRE_FLUSH2 not in texte:
    erreurs.append("ANCRE_FLUSH2 introuvable")
else:
    texte = texte.replace(ANCRE_FLUSH2, AJOUT_FLUSH2, 1)

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
    print("OK : dashboard/home.html compacte davantage (round 2).")