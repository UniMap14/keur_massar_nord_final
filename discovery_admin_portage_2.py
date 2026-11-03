# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

def bloc(motif, avant, apres, titre):
    for i, l in enumerate(lignes):
        if motif in l:
            debut = max(0, i - avant)
            fin = min(len(lignes), i + apres)
            print(f"=== {titre} (trouve ligne {i+1}) ===")
            for j in range(debut, fin):
                print(f"{j+1}: {repr(lignes[j])}")
            print()
            return
    print(f"=== {titre} : MOTIF '{motif}' INTROUVABLE ===\n")

bloc("let allZones", 1, 3, "declarations allZones/userLatLng")
bloc("afficherInfrastructuresProches();", 15, 3, "appel afficherInfrastructuresProches dans le callback geolocaliser")

def imprimer_fonction(nom_fonction, titre=None):
    debut = None
    for i, l in enumerate(lignes):
        if re.match(r"\s*function " + re.escape(nom_fonction) + r"\(", l):
            debut = i
            break
    if debut is None:
        print(f"{titre or nom_fonction} INTROUVABLE\n")
        return
    fin = len(lignes)
    niveau = 0
    compte_ouvert = False
    for j in range(debut, len(lignes)):
        niveau += lignes[j].count("{") - lignes[j].count("}")
        if "{" in lignes[j]:
            compte_ouvert = True
        if compte_ouvert and niveau <= 0:
            fin = j + 1
            break
    print(f"=== {titre or nom_fonction}, lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(repr(lignes[i]))
    print()

imprimer_fonction("construirePopupInfra")
imprimer_fonction("effacerSelection")
imprimer_fonction("afficherResultatSelection")
imprimer_fonction("analyserZonesSousDesservies")
imprimer_fonction("basculerVoronoi")

bloc("const centre = layer.getBounds().getCenter();", 2, 3, "fiche parcelle: const centre =")
bloc("Secteur</span>", 1, 2, "fiche parcelle: ligne Secteur")
bloc("L.marker([infra.latitude, infra.longitude]", 1, 4, "creation marqueur infra")
bloc("calculerSelection(forme);", 1, 2, "appel calculerSelection dans surFormeDessinee")
bloc("onEvent('btnSelectionEffacer'", 1, 2, "wiring btnSelectionEffacer")