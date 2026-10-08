# -*- coding: utf-8 -*-
"""
A lancer UNE FOIS avant importer_infrastructures_v2.py.

Cree les categories qui n'existent pas encore en base (notamment
"religion", nouvelle avec ce lot d'infrastructures). Les categories
deja existantes ne sont jamais modifiees (get_or_create).

Sans ce script, importer_infrastructures_v2.py ignorerait silencieusement
toute infrastructure dont la categorie n'existe pas encore.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from foncier.models import CategorieInfrastructure

CATEGORIES_REQUISES = {
    "education": {"label": "Éducation", "icone": "fa-graduation-cap", "couleur": "#2f7a4f"},
    "sante": {"label": "Santé", "icone": "fa-hospital", "couleur": "#b23b2e"},
    "commerce": {"label": "Commerce", "icone": "fa-store", "couleur": "#c9982e"},
    "sport_loisirs": {"label": "Sport & Loisirs", "icone": "fa-futbol", "couleur": "#3468a8"},
    "station_service": {"label": "Station-service", "icone": "fa-gas-pump", "couleur": "#6b4a35"},
    "transport": {"label": "Transport", "icone": "fa-bus", "couleur": "#766c5d"},
    "environnement": {"label": "Environnement", "icone": "fa-recycle", "couleur": "#4a9c6d"},
    "administration": {"label": "Administration", "icone": "fa-building-columns", "couleur": "#2b1e16"},
    "cimetiere": {"label": "Cimetière", "icone": "fa-cross", "couleur": "#5a5a5a"},
    "banque": {"label": "Banque", "icone": "fa-sack-dollar", "couleur": "#1f5c3a"},
    "securite": {"label": "Sécurité", "icone": "fa-shield-halved", "couleur": "#a3271e"},
    "energie": {"label": "Énergie", "icone": "fa-bolt", "couleur": "#d9a52b"},
    "socio_communautaire": {"label": "Socio-communautaire", "icone": "fa-people-group", "couleur": "#8a624a"},
    "hotellerie": {"label": "Hôtellerie", "icone": "fa-hotel", "couleur": "#7b3fa0"},
    "religion": {"label": "Lieux de culte", "icone": "fa-place-of-worship", "couleur": "#4a7c8a"},
}

for code, infos in CATEGORIES_REQUISES.items():
    categorie, cree = CategorieInfrastructure.objects.get_or_create(
        code=code,
        defaults={"label": infos["label"], "icone": infos["icone"], "couleur": infos["couleur"]},
    )
    if cree:
        print(f"OK : categorie CREEE '{code}' -> {infos['label']}")
    else:
        print(f"    deja presente : '{code}' -> {categorie.label} (inchangee)")

print(f"\n{CategorieInfrastructure.objects.count()} categorie(s) au total en base.")