# -*- coding: utf-8 -*-
"""
Import des infrastructures nettoyees (infrastructures_propres.csv) dans la
base Django : remplit categorie, quartier (rattachement spatial officiel),
sous_type et details (horaires, telephone, employes, services, etc.).

Vide et reconstruit entierement la table (le CSV est la source complete
et definitive des 133 infrastructures).

USAGE : placer infrastructures_propres.csv a la racine du projet, puis :
    python importer_infrastructures_v2.py
"""
import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmsn.settings")
django.setup()

from foncier.models import Infrastructure, CategorieInfrastructure

CHEMIN_CSV = "infrastructures_propres.csv"

LIBELLES = {
    "nom_responsable": "Responsable",
    "telephone": "Téléphone",
    "horaires": "Horaires",
    "garde_nuit": "Garde de nuit",
    "nombre_employes": "Nombre d'employés",
    "nombre_enseignants": "Nombre d'enseignants",
    "nombre_talibes": "Nombre de talibés",
    "nombre_salles": "Nombre de salles",
    "salle_accouchement": "Salle d'accouchement",
    "nombre_salles_accouchement": "Nombre de salles d'accouchement",
    "salle_hospitalisation": "Salle d'hospitalisation",
    "nombre_salles_hospitalisation": "Nombre de salles d'hospitalisation",
    "ambulance": "Ambulance",
    "nombre_ambulances": "Nombre d'ambulances",
    "nombre_lits": "Nombre de lits",
    "nombre_medecins": "Nombre de médecins",
    "nombre_personnel": "Nombre de personnel",
    "nombre_patients_jour": "Patients reçus/jour",
    "vaccination": "Vaccination",
    "consultations_prenatales": "Consultations prénatales",
    "services": "Services proposés",
    "nombre_lignes_transport": "Nombre de lignes",
    "nombre_comptoirs": "Nombre de comptoirs",
    "jours_marche": "Jours de marché",
    "salle_informatique": "Salle informatique",
}


def vide(v):
    return v is None or str(v).strip() == "" or str(v).strip().lower() == "nan"


nb_supprimees, _ = Infrastructure.objects.all().delete()
print(f"Anciennes infrastructures supprimees : {nb_supprimees}")

compteur_crees = 0
compteur_maj = 0
compteur_categorie_inconnue = 0

with open(CHEMIN_CSV, encoding="utf-8-sig") as f:
    lecteur = csv.DictReader(f)
    for ligne in lecteur:
        code_categorie = (ligne.get("categorie_code") or "").strip()
        try:
            categorie = CategorieInfrastructure.objects.get(code=code_categorie)
        except CategorieInfrastructure.DoesNotExist:
            compteur_categorie_inconnue += 1
            print(f"ATTENTION : categorie inconnue '{code_categorie}' pour {ligne.get('id_shp')} ({ligne.get('nom')})")
            continue

        details = {}
        for cle, libelle in LIBELLES.items():
            valeur = ligne.get(cle)
            if not vide(valeur):
                details[libelle] = str(valeur).strip()

        nom = ligne["nom"].strip() if not vide(ligne.get("nom")) else "(nom non renseigné)"
        quartier = ligne["quartier"].strip() if not vide(ligne.get("quartier")) else ""
        sous_type = ligne["sous_type"].strip() if not vide(ligne.get("sous_type")) else ""

        lat = float(ligne["latitude"]) if not vide(ligne.get("latitude")) else None
        lon = float(ligne["longitude"]) if not vide(ligne.get("longitude")) else None

        obj, cree = Infrastructure.objects.update_or_create(
            id_shp=ligne["id_shp"].strip(),
            defaults={
                "categorie": categorie,
                "nom": nom,
                "quartier": quartier,
                "sous_type": sous_type,
                "latitude": lat,
                "longitude": lon,
                "details": details,
            },
        )
        if cree:
            compteur_crees += 1
        else:
            compteur_maj += 1

print("\n=== Import terminé ===")
print(f"Créées : {compteur_crees}")
print(f"Mises à jour : {compteur_maj}")
print(f"Catégories inconnues (ignorées) : {compteur_categorie_inconnue}")
print(f"Total infrastructures en base : {Infrastructure.objects.count()}")