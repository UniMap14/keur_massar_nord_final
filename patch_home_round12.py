# -*- coding: utf-8 -*-
"""
Round 12 (home.html) : organise les tuiles de contenu exactement comme
l'image 2 (meme ordre, memes proportions relatives), via CSS Grid
"order" + "grid-column: span N" sur les classes cell-* deja presentes
dans le HTML -- aucune donnee, aucun bloc HTML deplace. Les 3 panneaux
reels absents de la maquette (paiements, retardataires, zones) sont
conserves sur une 3e ligne, pour ne rien supprimer.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Ajoute des classes cell-zones / cell-taxes aux 2 panneaux qui en
#    sont encore depourvus (actuellement juste class="panel")
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
# 2) Hauteur de ligne un peu reduite (3 lignes au lieu de 2 maintenant)
# ---------------------------------------------------------------------
ANCRE_HAUTEUR = """    .dashboard-grid {
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
AJOUT_HAUTEUR = """    .dashboard-grid {
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
    }"""
if "grid-auto-rows: 135px !important;" in texte:
    pass
elif ANCRE_HAUTEUR not in texte:
    erreurs.append("ANCRE_HAUTEUR introuvable")
else:
    texte = texte.replace(ANCRE_HAUTEUR, AJOUT_HAUTEUR, 1)

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
# 3) Organisation exacte (ordre + largeur de chaque tuile)
# ---------------------------------------------------------------------
ANCRE_FIN = """    .dashboard-grid .mini-map-stats { padding: 2px 6px !important; }
</style>
{% endblock %}"""
AJOUT_FIN = """    .dashboard-grid .mini-map-stats { padding: 2px 6px !important; }

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
    .dashboard-grid .cell-zones           { grid-column: span 2 !important; order: 12 !important; }
</style>
{% endblock %}"""
if "Organisation identique a l'image de reference (round 12)" in texte:
    pass
elif ANCRE_FIN not in texte:
    erreurs.append("ANCRE_FIN introuvable")
else:
    texte = texte.replace(ANCRE_FIN, AJOUT_FIN, 1)

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