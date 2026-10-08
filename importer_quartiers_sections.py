# -*- coding: utf-8 -*-
"""
Import des couches quartiers officiels et sections cadastrales.

USAGE : placer les dossiers "quartier" et "section" (contenant les .shp)
a la racine du projet, puis :
    python importer_quartiers_sections.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from django.contrib.gis.gdal import DataSource, CoordTransform, SpatialReference
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon

from foncier.models import QuartierOfficiel, SectionCadastrale


def enlever_z(geos_geom):
    """Retire la dimension Z (altitude) d'une geometrie 2D/3D, recursivement."""
    if not geos_geom.hasz:
        return geos_geom
    if geos_geom.geom_type == "Polygon":
        anneaux = [[(x, y) for x, y, *_ in anneau.coords] for anneau in geos_geom]
        return Polygon(*anneaux, srid=4326)
    if geos_geom.geom_type == "MultiPolygon":
        return MultiPolygon([enlever_z(p) for p in geos_geom], srid=4326)
    return geos_geom


def importer_couche(chemin_shp, champ_source, modele, champ_modele):
    ds = DataSource(chemin_shp)
    couche = ds[0]
    transform = CoordTransform(couche.srs, SpatialReference(4326))

    modele.objects.all().delete()
    compteur = 0
    ignores = 0

    for feature in couche:
        try:
            geom = feature.geom.clone()
            geom.transform(transform)
            geos_geom = GEOSGeometry(geom.wkt, srid=4326)
            geos_geom = enlever_z(geos_geom)

            if geos_geom.geom_type == "Polygon":
                geos_geom = MultiPolygon(geos_geom, srid=4326)
            elif geos_geom.geom_type != "MultiPolygon":
                ignores += 1
                continue

            valeur = feature.get(champ_source)
            obj = modele(geom=geos_geom)
            setattr(obj, champ_modele, str(valeur).strip() if valeur is not None else "")
            obj.save()
            compteur += 1
        except Exception as e:
            print(f"  ATTENTION : enregistrement ignore ({e})")
            ignores += 1

    print(f"{modele.__name__} : {compteur} importes, {ignores} ignores.")


print("=== Import quartiers officiels ===")
importer_couche("quartier/kmsn_quartier.shp", "QRT_VLG_HA", QuartierOfficiel, "nom")

print("\n=== Import sections cadastrales ===")
importer_couche("section/section.shp", "N section", SectionCadastrale, "numero")

print(f"\nTotal en base : {QuartierOfficiel.objects.count()} quartiers, {SectionCadastrale.objects.count()} sections.")