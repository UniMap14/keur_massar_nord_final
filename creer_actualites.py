# ============================================================
# creer_actualites.py
#
# Cree quelques actualites reelles pour la page d'accueil, basees sur
# de vraies informations publiques recentes concernant la commune de
# Keur Massar Nord (bilan du maire, evenement citoyen, projet prive
# d'envergure) -- reformulees dans nos propres mots, pas copiees.
#
# Reexecutable sans risque : si une actualite avec le meme titre
# existe deja, elle n'est pas recreee.
#
# UTILISATION :  python creer_actualites.py
# ============================================================

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

import datetime
from foncier.models import Actualite

ACTUALITES = [
    {
        "titre": "Bilan municipal : proximité et investissements sociaux depuis 2022",
        "chapo": (
            "Depuis son installation en 2022, l'équipe municipale met l'accent sur "
            "la proximité avec les habitants : nouveau bâtiment administratif, appui "
            "au sport communautaire et aides sociales élargies."
        ),
        "contenu": (
            "La commune a engagé la construction d'un bâtiment administratif moderne "
            "destiné à rapprocher les services municipaux des citoyens et à faciliter "
            "leurs démarches au quotidien.\n\n"
            "Le soutien au sport local occupe une place importante dans l'action "
            "municipale, avec un appui apporté à une trentaine d'associations sportives "
            "communales, aux académies de football et de handball, ainsi qu'au football "
            "féminin.\n\n"
            "Sur le plan social, plusieurs milliers de foyers ont bénéficié d'aides lors "
            "des grandes fêtes religieuses depuis 2022, et plus d'un millier de bourses "
            "d'études ou de formation ont été attribuées, aux côtés de centaines de "
            "permis de conduire subventionnés."
        ),
        "categorie": "COMMUNIQUE",
        "date_publication": datetime.date(2026, 2, 4),
    },
    {
        "titre": "La commune mobilisée pour la Journée citoyenne Set Setal Sunu Réew",
        "chapo": (
            "La municipalité a pris part à la journée nationale de salubrité "
            "Set Setal Sunu Réew, aux côtés des autres collectivités du département."
        ),
        "contenu": (
            "Dans le cadre de cette journée citoyenne organisée à l'échelle nationale, "
            "les autorités communales de Keur Massar Nord ont répondu présentes pour "
            "cette édition consacrée au nettoiement et à l'embellissement des espaces "
            "publics.\n\n"
            "L'opération a mobilisé les autorités du département aux côtés des "
            "populations, dans un esprit de solidarité et d'engagement citoyen pour "
            "un cadre de vie plus propre et plus sain."
        ),
        "categorie": "EVENEMENT",
        "date_publication": datetime.date(2026, 9, 6),
    },
    {
        "titre": "Un nouveau centre commercial et culturel attendu à Keur Massar Nord",
        "chapo": (
            "Un investissement privé de 185 millions de FCFA doit doter la commune "
            "d'un complexe moderne mêlant commerces, sport et espace culturel."
        ),
        "contenu": (
            "Porté par un entrepreneur local, ce projet de complexe R+2 doit accueillir "
            "plusieurs espaces commerciaux, une salle de musculation ainsi qu'une grande "
            "salle destinée aux événements culturels et communautaires.\n\n"
            "Dans une commune où l'emploi des jeunes et le manque d'espaces modernes "
            "restent des défis importants, cette initiative privée est accueillie comme "
            "une contribution bienvenue au dynamisme économique local. L'inauguration "
            "est annoncée pour la mi-juin 2026."
        ),
        "categorie": "PROJET",
        "date_publication": datetime.date(2026, 5, 25),
    },
]


def main():
    crees = 0
    for infos in ACTUALITES:
        if Actualite.objects.filter(titre=infos["titre"]).exists():
            print(f"DEJA PRESENT : {infos['titre']}")
            continue
        Actualite.objects.create(**infos)
        crees += 1
        print(f"OK : {infos['titre']}")

    print(f"\n=== {crees} actualite(s) creee(s). ===")


if __name__ == "__main__":
    main()