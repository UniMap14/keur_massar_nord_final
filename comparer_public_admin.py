# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with io.open("foncier/templates/foncier/geoportail.html", "r", encoding="utf-8") as f:
    public = f.read()
with io.open("foncier/templates/foncier/geoportail_admin.html", "r", encoding="utf-8") as f:
    admin = f.read()

marqueurs = [
    ("Choisir une destination sur la carte (itineraire libre)", "btnChoisirDestination"),
    ("Zone/quartier + ma parcelle sur Me geolocaliser", "afficherZoneEtParcelle"),
    ("Mes parcelles (citoyen connecte) transmises au template", "mes_parcelles_geojson"),
    ("Selection spatiale : quartiers touches + infra dans la zone", "selectionZones"),
    ("Selection spatiale : surlignage infra (point rouge)", "surlignerInfrastructure"),
    ("Itineraire vers la zone selectionnee", "btnSelectionItineraire"),
    ("Distance + itineraire dans le popup infrastructure", "infraRouteBtn"),
    ("Distance dans la fiche parcelle", "fpDistanceTexte"),
    ("Zones sous-desservies : respecte filtre categorie + limite commune + liste quartiers", "parcellesConcernees"),
    ("Zone tampon (choisir un point libre)", "btnRayonPointLibre"),
    ("Pression fonciere (taux de bati, non-batis proches, sans titre)", "btnAnalyserBati"),
]

print(f"{'Fonctionnalite':70} | Public | Admin")
print("-" * 95)
for nom, marqueur in marqueurs:
    dans_public = "OUI" if marqueur in public else "non"
    dans_admin = "OUI" if marqueur in admin else "non"
    print(f"{nom:70} | {dans_public:6} | {dans_admin}")