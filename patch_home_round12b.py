# -*- coding: utf-8 -*-
"""
Round 12 (home.html) -- version corrigee : organise les tuiles de
contenu exactement comme l'image 2 (ordre + largeur relative), via
CSS Grid "order" + "grid-column: span N". Ancre sur le bloc qu'on
vient de modifier a l'instant (pas sur la fin du fichier, qui varie
a cause des rounds 8/9 deja appliques).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Classes cell-zones / cell-taxes
# ---------------------------------------------------------------------
ANCRE_ZONES = """<div class="stats-charts-row cell-stats-row">
  <div class="panel">
    <div class="panel-header">
      <h2><i class="fa-solid fa-map-location-dot"></i> Taux de recouvrement par zone</h2>"""
AJOUT_ZONES = """<div class="stats-charts-row cell-stats-row">
  <div class="panel cell-zones">
    <div class="panel-header">
      <h2><i class="fa-solid fa-map-location-dot"></i> Taux de recouvrement par zone</h2>"""
if "cell-zones" in texte:
    pass
elif ANCRE_ZONES not in texte:
    erreurs.append("ANCRE_ZONES introuvable")
else:
    texte = texte.replace(ANCRE_ZONES, AJOUT_ZONES, 1)

ANCRE_TAXES = """  <div class="panel">
    <div class="panel-header">
      <h2><i class="fa-solid fa-chart-pie"></i>"""
AJOUT_TAXES = """  <div class="panel cell-taxes">
    <div class="panel-header">
      <h2><i class="fa-solid fa-chart-pie"></i>"""
if "cell-taxes" in texte:
    pass
elif ANCRE_TAXES not in texte:
    erreurs.append("ANCRE_TAXES introuvable")
else:
    texte = texte.replace(ANCRE_TAXES, AJOUT_TAXES, 1)

# ---------------------------------------------------------------------
# 2) Hauteur de ligne reduite (3 lignes desormais) + organisation,
#    ajoutees ensemble juste apres le bloc deja modifie au round 11.
# ---------------------------------------------------------------------
ANCRE = """    .dashboard-grid {
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
AJOUT = """    .dashboard-grid {
        grid-template-columns: repeat(6, 1fr) !important;
        grid-auto-rows: 135px !important;
        align-items: stretch !important;
        gap: 8px !important;
    }
    .dashboard-grid .panel,
    .dashboard-grid .geo-access-card {
        grid-column: auto !important;
        grid-row: auto !important;
        height: 135px !important;
        overflow: hidden !important;
        margin: 0 !important;
    }

    /* ===== Organisation identique a l'image de reference (round 12) ===== */
    .dashboard-grid .cell-geo-banner      { grid-column: span 2 !important; order: 1  !important; }
    .dashboard-grid .cell-taux            { grid-column: span 1 !important; order: 2  !important; }
    .dashboard-grid .cell-evolution       { grid-column: span 1 !important; order: 3  !important; }
    .dashboard-grid .cell-taxes           { grid-column: span 1 !important; order: 4  !important; }
    .dashboard-grid .cell-map             { grid-column: span 1 !important; order: 5  !important; }
    .dashboard-grid .cell-quick-actions   { grid-column: span 2 !important; order: 6  !important; }
    .dashboard-grid .cell-demandes        { grid-column: span 2 !important; order: 7  !important; }
    .dashboard-grid .cell-parcelle-recente{ grid-column: span 1 !important; order: 8  !important; }
    .dashboard-grid .cell-activite        { grid-column: span 1 !important; order: 9  !important; }
    .dashboard-grid .cell-paiements       { grid-column: span 2 !important; order: 10 !important; }
    .dashboard-grid .cell-retardataires   { grid-column: span 2 !important; order: 11 !important; }
    .dashboard-grid .cell-zones           { grid-column: span 2 !important; order: 12 !important; }"""
if "Organisation identique a l'image de reference (round 12)" in texte:
    pass
elif ANCRE not in texte:
    erreurs.append("ANCRE (hauteur+organisation) introuvable")
else:
    texte = texte.replace(ANCRE, AJOUT, 1)

ANCRE_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 92px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 68px !important; }
    .dashboard-grid .mini-map-stats { padding: 3px 6px !important; }"""
AJOUT_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 85px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 60px !important; }
    .dashboard-grid .mini-map-stats { padding: 2px 6px !important; }"""
if "height: 85px !important;" in texte:
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
    print("OK : dashboard/home.html -- round 12 (organisation des tuiles conforme a l'image 2).")