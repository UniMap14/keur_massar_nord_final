import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.core.files import File
from foncier.models import Actualite

ASSOCIATIONS = [
    ("Bilan municipal : proximité et investissements sociaux depuis 2022", "actu1.jpg"),
    ("La commune mobilisée pour la Journée citoyenne Set Setal Sunu Réew", "actu2.jpg"),
    ("Un nouveau centre commercial et culturel attendu à Keur Massar Nord", "actu3.jpg"),
]


def main():
    for titre, nom_fichier in ASSOCIATIONS:
        try:
            actualite = Actualite.objects.get(titre=titre)
        except Actualite.DoesNotExist:
            print(f"INTROUVABLE (actualité) : {titre}")
            continue

        if not os.path.exists(nom_fichier):
            print(f"INTROUVABLE (fichier) : {nom_fichier} -- placez-le a la racine du projet.")
            continue

        with open(nom_fichier, "rb") as f:
            actualite.photo.save(nom_fichier, File(f), save=True)

        print(f"OK : {nom_fichier} attaché à « {titre} »")


if __name__ == "__main__":
    main()