# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi_echelle.py', encoding='utf-8').read())"

Objectif : estimer l'ampleur du calcul cote navigateur (combien de
cellules de grille, combien d'infrastructures) pour savoir si le vrai
goulot d'etranglement est le nombre d'infrastructures (recherche du
plus proche voisin) ou le nombre de cellules (taille de la commune).
"""
from django.contrib.gis.db.models import Extent
from foncier.models import Infrastructure, Parcelle

nb_infra = Infrastructure.objects.filter(latitude__isnull=False, longitude__isnull=False).count()
print("Nombre d'infrastructures geolocalisees :", nb_infra)

etendue = Parcelle.objects.exclude(geom__isnull=True).aggregate(e=Extent("geom"))["e"]
if etendue:
    west, south, east, north = etendue
    largeur_deg = east - west
    hauteur_deg = north - south
    pas = 0.0018
    nb_cellules_approx = (largeur_deg / pas) * (hauteur_deg / pas)
    print(f"Emprise : largeur {largeur_deg:.4f} deg, hauteur {hauteur_deg:.4f} deg")
    print(f"Nombre de cellules de grille (pas de 180m), avant filtrage 'dans la commune' : ~{int(nb_cellules_approx)}")
    print(f"Nombre d'operations distance (cellules x infra), ordre de grandeur : ~{int(nb_cellules_approx * nb_infra):,}")
else:
    print("Impossible de calculer l'emprise.")