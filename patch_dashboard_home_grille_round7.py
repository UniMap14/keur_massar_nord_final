# -*- coding: utf-8 -*-
"""
Round 7 :
1) CartoDB (basemaps.cartocdn.com) exige desormais une cle API pour ses
   tuiles gratuites -- la tuile affichait un texte "API Key"/"carto.co"
   a la place du fond de carte. On passe a Esri World Street Map
   (server.arcgisonline.com), gratuit sans cle, domaine different.
2) Les titres de panneaux passaient sur plusieurs lignes et mangeaient
   toute la hauteur de la tuile (coupant le graphique en donut
   notamment). On force une seule ligne avec troncature (...) et on
   reduit le bouton "Voir tout".

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Fournisseur de tuiles : CartoDB -> Esri World Street Map
# ---------------------------------------------------------------------
ANCRE_TUILES = """        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 18,
            subdomains: 'abcd',
        }).addTo(miniMap);"""
AJOUT_TUILES = """        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19,
        }).addTo(miniMap);"""
if "arcgisonline.com" in texte:
    pass
elif ANCRE_TUILES not in texte:
    erreurs.append("ANCRE_TUILES introuvable")
else:
    texte = texte.replace(ANCRE_TUILES, AJOUT_TUILES, 1)

# ---------------------------------------------------------------------
# 2) Titres de panneaux sur une seule ligne (troncature) + bouton
#    "Voir tout" plus petit, pour ne plus manger la hauteur des tuiles.
# ---------------------------------------------------------------------
ANCRE_HEADER_H2 = """    .dashboard-grid .panel-header h2 {
        font-size: 12.5px !important;
        margin: 0 !important;
    }"""
AJOUT_HEADER_H2 = """    .dashboard-grid .panel-header h2 {
        font-size: 11.5px !important;
        margin: 0 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: flex !important;
        min-width: 0 !important;
    }
    .dashboard-grid .panel-header h2 i { flex-shrink: 0 !important; }
    .dashboard-grid .panel-header {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 6px !important;
    }
    .dashboard-grid .panel-header .btn {
        font-size: 9px !important;
        padding: 2px 7px !important;
        flex-shrink: 0 !important;
        white-space: nowrap !important;
    }"""
if "text-overflow: ellipsis !important;" in texte:
    pass
elif ANCRE_HEADER_H2 not in texte:
    erreurs.append("ANCRE_HEADER_H2 introuvable")
else:
    texte = texte.replace(ANCRE_HEADER_H2, AJOUT_HEADER_H2, 1)

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
    print("OK : dashboard/home.html -- round 7 (tuiles Esri + titres sur une seule ligne).")