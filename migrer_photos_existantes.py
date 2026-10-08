# -*- coding: utf-8 -*-
"""
Copie les 5 photos actuellement codees en dur (foncier/static/foncier/img/gallery/)
vers la nouvelle table PhotoGalerie, pour qu'elles continuent d'apparaitre sur le
site apres le passage a la gestion dynamique. A lancer UNE SEULE FOIS.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from django.core.files import File
from foncier.models import PhotoGalerie

DOSSIER_SOURCE = "foncier/static/foncier/img/gallery"

PHOTOS = [
    ("panneau-entree-commune.jpeg", "Entrée de la Commune de Keur Massar Nord", 1),
    ("mairie-batiment.jpeg", "Bâtiment de la mairie", 2),
    ("marche-commerces.jpg", "Marché et commerces animés", 3),
    ("circulation-pont.jpeg", "Axes routiers et circulation", 4),
    ("centre-services-fiscaux.jpeg", "Centre des services fiscaux (DGID)", 5),
]

if PhotoGalerie.objects.exists():
    print("IGNORE : la galerie contient deja des photos, rien n'a ete importe.")
    print(f"({PhotoGalerie.objects.count()} photo(s) deja en base)")
else:
    for nom_fichier, titre, ordre in PHOTOS:
        chemin = os.path.join(DOSSIER_SOURCE, nom_fichier)
        if not os.path.exists(chemin):
            print(f"ATTENTION : fichier introuvable, ignore -> {chemin}")
            continue
        with open(chemin, "rb") as f:
            photo = PhotoGalerie(titre=titre, ordre=ordre)
            photo.photo.save(nom_fichier, File(f), save=True)
        print(f"OK : « {titre} » importee.")

    print(f"\nTermine : {PhotoGalerie.objects.count()} photo(s) en base.")