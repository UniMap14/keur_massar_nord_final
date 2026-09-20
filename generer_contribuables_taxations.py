# ============================================================
# generer_contribuables_taxations.py
#
# Complète la simulation fiscale foncière (déjà appliquée aux
# parcelles via simuler_fiscalite_fonciere.py) en créant les
# Contribuable/Taxation/Paiement correspondants, pour peupler
# entièrement le tableau de bord admin.
#
# PRINCIPE D'HONNÊTETÉ : aucune identité de personne n'est inventée.
# Le vrai rattachement propriétaire (355 candidats identifiés lors
# d'un import précédent) ne s'applique plus au jeu de parcelles
# actuel. Chaque Contribuable créé ici porte donc explicitement le
# nom "Propriétaire non identifié" — jamais un nom fabriqué — ce qui
# reflète d'ailleurs une réalité documentée par l'enquête de terrain
# (difficulté d'identification des propriétaires).
#
# Chaque Taxation créée est marquée simulation_fiscale=True.
#
# TAUX DE RECOUVREMENT SIMULÉ : l'enquête de terrain a confirmé que
# le service fiscal local ne dispose d'AUCUNE donnée sur le taux de
# recouvrement réel ("Ils peuvent pas avoir des données"). Faute de
# référence, un taux illustratif de 30% de paiement est retenu ici,
# à documenter explicitement comme hypothèse non sourcée dans le
# mémoire (contrairement aux taux CFPB/CFPNB, qui eux sont réels).
#
# Réexécutable sans risque : ignore les parcelles qui ont déjà une
# Taxation simulée associée.
#
# UTILISATION :  python generer_contribuables_taxations.py
# ============================================================

import os
import random
import datetime
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmsn.settings')
django.setup()

from django.db import transaction
from foncier.models import Parcelle, Contribuable, Taxation, TypeTaxe, Paiement

TAUX_PAIEMENT_SIMULE = 0.30  # illustratif, non sourcé — voir en-tête
ANNEE_FISCALE = 2026

random.seed(42)  # résultat reproductible d'un lancement à l'autre


def main():
    try:
        type_taxe_fonciere = TypeTaxe.objects.get(code="FONCIERE")
    except TypeTaxe.DoesNotExist:
        print("ERREUR : le type de taxe 'FONCIERE' n'existe pas.")
        print("Lancez d'abord : python seed_types_taxe.py")
        return

    ids_parcelles_deja_traitees = Taxation.objects.filter(
        simulation_fiscale=True, parcelle__isnull=False
    ).values_list("parcelle_id", flat=True)

    parcelles_a_traiter = (
        Parcelle.objects
        .filter(simulation_fiscale=True)
        .exclude(id__in=list(ids_parcelles_deja_traitees))
        .filter(montant_taxe_annuelle__gt=0)
    )

    total_candidates = parcelles_a_traiter.count()
    print(f"{total_candidates} parcelle(s) simulée(s) sans Taxation associée.\n")

    n_crees = 0
    n_payees = 0
    dernier_numero = Contribuable.objects.filter(numero_fiscal__startswith="SIMU-").count()

    with transaction.atomic():
        for parcelle in parcelles_a_traiter.iterator():
            dernier_numero += 1
            numero_fiscal = f"SIMU-{dernier_numero:06d}"

            contribuable = Contribuable.objects.create(
                numero_fiscal=numero_fiscal,
                nom="Propriétaire non identifié",
                prenom="",
                telephone="",
            )

            taxation = Taxation.objects.create(
                contribuable=contribuable,
                type_taxe=type_taxe_fonciere,
                parcelle=parcelle,
                montant_du=parcelle.montant_taxe_annuelle,
                annee_fiscale=ANNEE_FISCALE,
                simulation_fiscale=True,
            )
            n_crees += 1

            a_paye = random.random() < TAUX_PAIEMENT_SIMULE
            if a_paye:
                jours_avant = random.randint(5, 200)
                date_paiement = datetime.date.today() - datetime.timedelta(days=jours_avant)
                numero_recu = f"REC-SIMU-{dernier_numero:06d}"
                Paiement.objects.create(
                    taxation=taxation,
                    montant=taxation.montant_du,
                    date_paiement=date_paiement,
                    mode_paiement="ESPECES",
                    statut_paiement="CONFIRME",
                    numero_recu=numero_recu,
                )
                parcelle.statut_fiscal = "A_JOUR"
                n_payees += 1
            else:
                parcelle.statut_fiscal = "EN_RETARD"

            parcelle.save(update_fields=["statut_fiscal"])

    print("=== Résumé ===")
    print(f"  Contribuables créés : {n_crees}")
    print(f"  Taxations créées : {n_crees}")
    print(f"  Dont payées (simulation, {TAUX_PAIEMENT_SIMULE*100:.0f}%) : {n_payees}")
    print(f"  Dont en retard : {n_crees - n_payees}")
    print()
    print("⚠️  Rappel : identités 'Propriétaire non identifié' honnêtes (aucun nom")
    print("   inventé), taux de paiement 30% illustratif et NON sourcé (à documenter")
    print("   comme hypothèse simplificatrice dans le mémoire).")


if __name__ == "__main__":
    main()