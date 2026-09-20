# ============================================================
# seed_types_taxe.py
#
# Crée les 6 types de taxe communale de base, si absents. Nécessaire
# au bon fonctionnement de la page publique Fiscalité (calendrier des
# échéances) et du dashboard admin (Types de taxe, Taxations).
#
# Réexécutable sans risque : utilise get_or_create, ne duplique jamais.
#
# UTILISATION :  python seed_types_taxe.py
# ============================================================

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from foncier.models import TypeTaxe

TYPES = [
    {
        "code": "FONCIERE",
        "libelle": "Taxe foncière communale",
        "mois_echeance": 3,
        "jour_echeance": 31,
        "penalite_retard": 10,
    },
    {
        "code": "PATENTE",
        "libelle": "Patente locale",
        "mois_echeance": 2,
        "jour_echeance": 28,
        "penalite_retard": 10,
    },
    {
        "code": "OCCUPATION",
        "libelle": "Taxe d'occupation du domaine public",
        "mois_echeance": 1,
        "jour_echeance": 31,
        "penalite_retard": 10,
    },
    {
        "code": "MARCHE",
        "libelle": "Taxe sur les marchés",
        "mois_echeance": 12,
        "jour_echeance": 31,
        "penalite_retard": 5,
    },
    {
        "code": "ASSAINISSEMENT",
        "libelle": "Redevance d'assainissement",
        "mois_echeance": 6,
        "jour_echeance": 30,
        "penalite_retard": 5,
    },
    {
        "code": "PUBLICITE",
        "libelle": "Taxe sur la publicité",
        "mois_echeance": 4,
        "jour_echeance": 30,
        "penalite_retard": 10,
    },
]


def main():
    n_crees = 0
    n_deja_presents = 0
    for infos in TYPES:
        obj, cree = TypeTaxe.objects.get_or_create(
            code=infos["code"],
            defaults={
                "libelle": infos["libelle"],
                "mois_echeance": infos["mois_echeance"],
                "jour_echeance": infos["jour_echeance"],
                "penalite_retard": infos["penalite_retard"],
            },
        )
        if cree:
            n_crees += 1
            print(f"  Créé : {obj.code} — {obj.libelle}")
        else:
            n_deja_presents += 1
            print(f"  Déjà présent : {obj.code} — {obj.libelle}")

    print()
    print(f"=== Résumé : {n_crees} créé(s), {n_deja_presents} déjà présent(s) ===")
    print(f"Total en base : {TypeTaxe.objects.count()} type(s) de taxe.")


if __name__ == "__main__":
    main()