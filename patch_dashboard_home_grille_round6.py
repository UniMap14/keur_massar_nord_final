# -*- coding: utf-8 -*-
"""
Round 6 :
1) Reduit encore la hauteur des tuiles de la grille 6 colonnes (il
   restait de la place vide dans chaque tuile), pour eliminer le
   defilement residuel et que tout tienne sur un seul ecran.
2) Change le fournisseur de tuiles de la mini-carte : OpenStreetMap
   (tile.openstreetmap.org) est bloque par un bloqueur de
   pub/traqueurs cote navigateur ("Blocked" affiche a la place du fond
   de carte) -- on passe a CartoDB (basemaps.cartocdn.com), un domaine
   different, generalement pas cible par les listes de blocage.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Tuiles plus basses (160px -> 115px) + elements internes reduits
# ---------------------------------------------------------------------
ANCRE_HAUTEUR = """    .kpi-grid,
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
    }"""
AJOUT_HAUTEUR = """    .kpi-grid,
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
if "grid-auto-rows: 115px !important;" in texte:
    pass
elif ANCRE_HAUTEUR not in texte:
    erreurs.append("ANCRE_HAUTEUR introuvable")
else:
    texte = texte.replace(ANCRE_HAUTEUR, AJOUT_HAUTEUR, 1)

# ---------------------------------------------------------------------
# 2) Graphiques et mini-carte encore plus compacts pour rentrer dans
#    les tuiles de 115px
# ---------------------------------------------------------------------
ANCRE_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 95px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 80px !important; }
    .dashboard-grid .mini-map-stats { padding: 4px 6px !important; }"""
AJOUT_CHARTS = """    .dashboard-grid .chart-wrap,
    .dashboard-grid .chart-wrap-sm {
        height: 62px !important;
    }
    .dashboard-grid .mini-map-canvas { height: 45px !important; }
    .dashboard-grid .mini-map-stats { padding: 2px 6px !important; }"""
if "height: 62px !important;" in texte:
    pass
elif ANCRE_CHARTS not in texte:
    erreurs.append("ANCRE_CHARTS introuvable")
else:
    texte = texte.replace(ANCRE_CHARTS, AJOUT_CHARTS, 1)

# ---------------------------------------------------------------------
# 3) En-tetes de panneaux encore plus fins
# ---------------------------------------------------------------------
ANCRE_HEADER = """    .dashboard-grid .panel-header {
        padding: 8px 12px !important;
        min-height: 0 !important;
    }"""
AJOUT_HEADER = """    .dashboard-grid .panel-header {
        padding: 4px 10px !important;
        min-height: 0 !important;
    }"""
if "padding: 4px 10px !important;\n        min-height: 0 !important;" in texte:
    pass
elif ANCRE_HEADER not in texte:
    erreurs.append("ANCRE_HEADER introuvable")
else:
    texte = texte.replace(ANCRE_HEADER, AJOUT_HEADER, 1)

# ---------------------------------------------------------------------
# 4) Fournisseur de tuiles : OpenStreetMap -> CartoDB (moins souvent
#    bloque par les bloqueurs de pub/traqueurs)
# ---------------------------------------------------------------------
ANCRE_TUILES = """        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
        }).addTo(miniMap);"""
AJOUT_TUILES = """        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 18,
            subdomains: 'abcd',
        }).addTo(miniMap);"""
if "basemaps.cartocdn.com" in texte:
    pass
elif ANCRE_TUILES not in texte:
    erreurs.append("ANCRE_TUILES introuvable")
else:
    texte = texte.replace(ANCRE_TUILES, AJOUT_TUILES, 1)

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
    print("OK : dashboard/home.html -- round 6 (tuiles plus basses + tuiles cartographiques CartoDB).")