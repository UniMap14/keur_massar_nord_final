# -*- coding: utf-8 -*-
"""
Import de la limite administrative de la commune (Keur Massar Nord).

USAGE : placer le dossier "mouh" (contenant kmsnn.shp et compagnie)
a la racine du projet, puis :
    python importer_limite.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from django.contrib.gis.gdal import DataSource, CoordTransform, SpatialReference
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon

from foncier.models import LimiteAdministrative


def enlever_z(geos_geom):
    if not geos_geom.hasz:
        return geos_geom
    if geos_geom.geom_type == "Polygon":
        anneaux = [[(x, y) for x, y, *_ in anneau.coords] for anneau in geos_geom]
        return Polygon(*anneaux, srid=4326)
    if geos_geom.geom_type == "MultiPolygon":
        return MultiPolygon([enlever_z(p) for p in geos_geom], srid=4326)
    return geos_geom


ds = DataSource("mouh/kmsnn.shp")
couche = ds[0]
transform = CoordTransform(couche.srs, SpatialReference(4326))

LimiteAdministrative.objects.all().delete()
compteur = 0

for feature in couche:
    geom = feature.geom.clone()
    geom.transform(transform)
    geos_geom = GEOSGeometry(geom.wkt, srid=4326)
    geos_geom = enlever_z(geos_geom)

    if geos_geom.geom_type == "Polygon":
        geos_geom = MultiPolygon(geos_geom, srid=4326)

    nom = feature.get("NOM_COMMUN") or "Keur Massar Nord"
    LimiteAdministrative.objects.create(nom=str(nom).strip(), geom=geos_geom)
    compteur += 1

print(f"LimiteAdministrative : {compteur} importee(s).")
print(f"Total en base : {LimiteAdministrative.objects.count()}")