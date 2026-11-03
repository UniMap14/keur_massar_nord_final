# -*- coding: utf-8 -*-
from foncier.models import Parcelle, QuartierOfficiel, SectionCadastrale, LimiteAdministrative, Infrastructure

print("=== Nombre d'enregistrements ===")
print("Parcelle (total) :", Parcelle.objects.count())
print("Parcelle (actives, geom non nulle) :", Parcelle.objects.exclude(geom__isnull=True).filter(parcelle_active=True).count())
print("QuartierOfficiel :", QuartierOfficiel.objects.count())
print("SectionCadastrale :", SectionCadastrale.objects.count())
print("LimiteAdministrative :", LimiteAdministrative.objects.count())
print("Infrastructure :", Infrastructure.objects.count())

def taille_geojson(qs):
    total = 0
    for obj in qs:
        total += len(obj.geom.geojson)
    return total

print()
print("=== Taille approx. du GeoJSON brut (non simplifie) ===")
print("Zones (octets) :", taille_geojson(QuartierOfficiel.objects.all()))
print("Sections (octets) :", taille_geojson(SectionCadastrale.objects.all()))
print("Limites (octets) :", taille_geojson(LimiteAdministrative.objects.all()))