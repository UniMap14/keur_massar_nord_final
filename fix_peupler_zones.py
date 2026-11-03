# -*- coding: utf-8 -*-
"""
Peuple le modele Zone (page "Zones" du menu Foncier, actuellement vide)
a partir de QuartierOfficiel (86 quartiers deja en base, avec geometrie),
puis assigne chaque Parcelle a sa zone par jointure spatiale (le
centroide de la parcelle tombe dans le polygone de la zone).

A executer UNE SEULE FOIS, depuis la racine du projet (a cote de
manage.py) :

    python manage.py shell -c "exec(open('fix_peupler_zones.py', encoding='utf-8').read())"

Le script est idempotent pour la partie "creation des zones" (il ne
recree pas une zone qui existe deja, identifiee par id_shp = pk du
QuartierOfficiel). La jointure spatiale, elle, peut etre relancee sans
risque : elle se contente de reecrire parcelle.zone_id.
"""
from django.db import connection
from foncier.models import Zone, QuartierOfficiel, Parcelle

print("=" * 100)
print("1) Copie des QuartierOfficiel -> Zone")
print("=" * 100)

existants = set(Zone.objects.values_list("id_shp", flat=True))
crees = 0
for q in QuartierOfficiel.objects.all():
    if q.pk in existants:
        continue
    Zone.objects.create(
        id_shp=q.pk,
        nom=q.nom,
        layer="QuartierOfficiel",
        path="genere_depuis_QuartierOfficiel",
        geom=q.geom,
    )
    crees += 1

print(f"  {crees} zone(s) creee(s) (sur {QuartierOfficiel.objects.count()} quartiers officiels).")
print(f"  Total Zone en base maintenant : {Zone.objects.count()}")
print()

print("=" * 100)
print("2) Jointure spatiale : assigner chaque Parcelle a la Zone qui contient son centroide")
print("=" * 100)

with connection.cursor() as cursor:
    cursor.execute("""
        UPDATE foncier_parcelle AS p
        SET zone_id = z.id
        FROM foncier_zone AS z
        WHERE ST_Contains(z.geom, ST_Centroid(p.geom))
    """)
    nb_mis_a_jour = cursor.rowcount

print(f"  {nb_mis_a_jour} parcelle(s) mise(s) a jour avec une zone.")
print()

print("=" * 100)
print("3) Bilan final")
print("=" * 100)
total_parcelles = Parcelle.objects.count()
avec_zone = Parcelle.objects.exclude(zone__isnull=True).count()
print(f"  Total parcelles       : {total_parcelles}")
print(f"  Parcelles avec zone   : {avec_zone}")
print(f"  Parcelles SANS zone   : {total_parcelles - avec_zone}  (hors des 86 polygones, ou geometrie invalide)")
print()
print("Termine. Rechargez la page 'Zones' dans l'admin.")