# ============================================================
# import_parcelles.py
#
# Importe le shapefile cadastral "keur_massar_nord_final" (40 588
# polygones parcellaires) directement dans la table Parcelle, en
# lisant le .shp via GDAL (déjà configuré sur ce poste pour PostGIS,
# donc aucune dépendance supplémentaire).
#
# UTILISATION :
#   1. Copier les 5 fichiers du shapefile (.shp .shx .dbf .prj .cpg)
#      quelque part dans le projet, par exemple dans un dossier
#      "shapefiles_a_importer/keur_massar_nord_final.shp" à la racine.
#   2. Adapter la variable CHEMIN_SHAPEFILE ci-dessous si besoin.
#   3. Lancer :  python import_parcelles.py
#
# CE QUE FAIT LE SCRIPT :
#   - Lit chaque polygone du shapefile (SRID source EPSG:32628) et le
#     transforme automatiquement vers EPSG:4326 (celui utilisé par
#     Parcelle.geom), via GDAL.
#   - Détermine le NICAD/numéro de parcelle avec la priorité suivante
#     (la plus fiable en premier) :
#       1. NICAD_MX      (rattachement matrice fiable — 355 cas)
#       2. NUMPARC_MX     (numéro lu sur le plan — 34 284 cas)
#       3. Numero_lot     (numéro de lot fiable via l'arrêté)
#       4. ID_UNIQUE      (identifiant technique du polygone, TOUJOURS
#                          présent — garantit qu'aucune parcelle n'est
#                          sautée même sans aucun numéro lisible)
#   - Remplit reference_arrete / occupation_sol directement depuis
#     Arrete / OCC_SOL (champs déjà prévus dans le modèle Parcelle).
#   - N'AFFECTE JAMAIS de propriétaire automatiquement : la mise en
#     correspondance avec la matrice cadastrale contient des cas
#     ambigus (voir LISEZ_MOI.md fourni avec le shapefile), et un CNI
#     est obligatoire sur Propriétaire alors que le shapefile n'en a
#     pas. Les parcelles sont importées SANS propriétaire ; un rapport
#     CSV séparé liste les correspondances les plus fiables trouvées,
#     à vérifier et lier manuellement par un agent depuis le dashboard.
#   - Ré-exécutable sans risque : les polygones déjà importés (même
#     ID_UNIQUE) sont ignorés, donc relancer le script après une mise
#     à jour du shapefile n'introduit pas de doublons.
# ============================================================

import os
import csv

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from foncier.models import Parcelle

CHEMIN_SHAPEFILE = "shapefiles_a_importer/keur_massar_nord_final.shp"
TAILLE_LOT = 2000  # nombre de parcelles insérées par lot (bulk_create)
RAPPORT_CSV = "parcelles_candidats_proprietaire_a_verifier.csv"


def valeur_ou_vide(feature, nom_champ):
    """Lit un champ GDAL en le nettoyant (None -> chaîne vide)."""
    try:
        val = feature.get(nom_champ)
    except Exception:
        return ""
    if val is None:
        return ""
    return str(val).strip()


def resoudre_nicad(feature):
    """Applique la priorité de fiabilité documentée dans LISEZ_MOI.md."""
    for champ in ("NICAD_MX", "NUMPARC_MX", "Numero_lot"):
        val = valeur_ou_vide(feature, champ)
        if val:
            return val
    # Dernier recours : toujours présent, garantit qu'aucun polygone
    # n'est sauté même sans numéro de parcelle lisible sur le plan.
    return valeur_ou_vide(feature, "ID_UNIQUE")


def vers_multipolygon(geom_gdal, srid_source):
    """Convertit une géométrie GDAL (Polygon ou MultiPolygon, en
    EPSG:32628) en MultiPolygon GEOS reprojeté en EPSG:4326."""
    geos_geom = GEOSGeometry(geom_gdal.wkt, srid=srid_source)
    geos_geom.transform(4326)
    if isinstance(geos_geom, Polygon):
        return MultiPolygon(geos_geom)
    return geos_geom


def main():
    if not os.path.exists(CHEMIN_SHAPEFILE):
        print(f"ERREUR : fichier introuvable : {CHEMIN_SHAPEFILE}")
        print("Vérifiez le chemin dans CHEMIN_SHAPEFILE en haut du script.")
        return

    ds = DataSource(CHEMIN_SHAPEFILE)
    couche = ds[0]
    srid_source = couche.srs.srid or 32628
    total_source = len(couche)
    print(f"Shapefile ouvert : {total_source} entités, SRID source détecté : {srid_source}")

    deja_importes = set(
        Parcelle.objects.exclude(id_shp__isnull=True).exclude(id_shp="")
        .values_list("id_shp", flat=True)
    )
    print(f"Déjà présentes en base (id_shp) : {len(deja_importes)}")

    a_creer = []
    candidats_proprietaire = []
    n_importees = 0
    n_ignorees_deja_presentes = 0
    n_erreurs = 0

    for feature in couche:
        id_unique = valeur_ou_vide(feature, "ID_UNIQUE")

        if id_unique in deja_importes:
            n_ignorees_deja_presentes += 1
            continue

        try:
            geom = vers_multipolygon(feature.geom, srid_source)
        except Exception as e:
            n_erreurs += 1
            print(f"  ! Géométrie ignorée pour {id_unique} : {e}")
            continue

        superficie_brute = feature.get("SUP_M2")
        superficie = float(superficie_brute) if superficie_brute else 0.0

        a_creer.append(Parcelle(
            id_shp=id_unique,
            nicad=resoudre_nicad(feature),
            superficie=superficie,
            reference_arrete=valeur_ou_vide(feature, "Arrete"),
            occupation_sol=valeur_ou_vide(feature, "OCC_SOL"),
            geom=geom,
        ))

        niveau_cf = valeur_ou_vide(feature, "NIVEAU_CF")
        if niveau_cf == "CANDIDAT_UNIQUE_FORT":
            candidats_proprietaire.append({
                "id_shp": id_unique,
                "nicad": resoudre_nicad(feature),
                "titulaire_matrice": valeur_ou_vide(feature, "TITULAIRE"),
                "nicad_matrice": valeur_ou_vide(feature, "NICAD_MX"),
                "code_section": valeur_ou_vide(feature, "CODESEC_MX"),
                "lotissement": valeur_ou_vide(feature, "LOTISSE_MX"),
            })

        if len(a_creer) >= TAILLE_LOT:
            Parcelle.objects.bulk_create(a_creer)
            n_importees += len(a_creer)
            print(f"  ... {n_importees} parcelles importées")
            a_creer = []

    if a_creer:
        Parcelle.objects.bulk_create(a_creer)
        n_importees += len(a_creer)

    # Rapport CSV des candidats de rattachement propriétaire les plus
    # fiables (355 cas), pour vérification manuelle par un agent.
    if candidats_proprietaire:
        with open(RAPPORT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(candidats_proprietaire[0].keys()), delimiter=";")
            writer.writeheader()
            writer.writerows(candidats_proprietaire)

    print()
    print("=== Résumé ===")
    print(f"  Parcelles importées      : {n_importees}")
    print(f"  Déjà présentes (ignorées): {n_ignorees_deja_presentes}")
    print(f"  Erreurs de géométrie     : {n_erreurs}")
    print(f"  Total en base après import : {Parcelle.objects.count()}")
    if candidats_proprietaire:
        print(f"  Candidats propriétaire à vérifier : {len(candidats_proprietaire)}")
        print(f"  -> voir le fichier {RAPPORT_CSV}")


if __name__ == "__main__":
    main()
