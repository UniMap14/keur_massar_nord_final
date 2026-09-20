# ============================================================
# foncier/management/commands/emettre_role_annuel.py
#
# Emet automatiquement le role fiscal de l'annee cible : pour chaque
# combinaison (parcelle, type de taxe) deja taxee une annee
# precedente, cree une nouvelle Taxation pour l'annee cible si elle
# n'existe pas encore -- en reprenant le meme montant que la derniere
# taxation connue (role "reconduit", comme en pratique reelle tant
# qu'aucune reevaluation n'a eu lieu).
#
# IMPORTANT : suit toujours le PROPRIETAIRE ACTUEL de la parcelle
# (Parcelle.proprietaire), pas l'ancien contribuable historique -- une
# mutation fiscale (DemandeMutation validee) change le proprietaire
# d'une parcelle, et le role de l'annee suivante doit alors etre emis
# au nom du nouveau proprietaire, pas de l'ancien. Repli sur l'ancien
# contribuable connu uniquement si la parcelle n'a pas (ou plus) de
# proprietaire identifiable.
#
# Ne touche JAMAIS aux taxations deja existantes (paiements, statuts,
# recours...) : cree uniquement les nouvelles, la ou il en manque.
# Saute automatiquement les parcelles exonerees (DemandeExoneration
# validee -> Parcelle.statut_fiscal == 'EXONERE').
# Reexecutable sans risque : les combinaisons deja emises pour
# l'annee cible sont simplement ignorees.
#
# UTILISATION :
#   python manage.py emettre_role_annuel                # annee en cours
#   python manage.py emettre_role_annuel --annee 2027   # annee precise
#
# A executer une fois par an (typiquement en debut d'annee fiscale) --
# voir LISEZ-MOI-taches-automatiques.md pour la configuration du
# Planificateur de taches Windows (aucun cron sous Windows).
# ============================================================

import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max

from foncier.models import Taxation, Parcelle, Contribuable


class Command(BaseCommand):
    help = "Emet automatiquement le role fiscal annuel (nouvelle Taxation pour chaque bien deja taxe, si pas encore emise pour l'annee cible)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--annee', type=int, default=None,
            help="Annee fiscale a emettre (par defaut : annee en cours).",
        )

    def handle(self, *args, **options):
        annee_cible = options['annee'] or datetime.date.today().year

        # Regroupe par (parcelle, type_taxe) SEUL -- plus par
        # contribuable -- pour pouvoir determiner le contribuable
        # ACTUEL a chaque passage (suit une eventuelle mutation).
        dernieres = (
            Taxation.objects
            .filter(annee_fiscale__lt=annee_cible)
            .values('parcelle_id', 'type_taxe_id')
            .annotate(derniere_annee=Max('annee_fiscale'))
        )

        n_crees = 0
        n_deja_present = 0
        n_ignores = 0
        n_exonerees = 0
        n_mutations_suivies = 0

        with transaction.atomic():
            for entree in dernieres:
                parcelle_id = entree['parcelle_id']
                type_taxe_id = entree['type_taxe_id']

                source = (
                    Taxation.objects
                    .filter(
                        parcelle_id=parcelle_id,
                        type_taxe_id=type_taxe_id,
                        annee_fiscale=entree['derniere_annee'],
                    )
                    .select_related('parcelle')
                    .first()
                )
                if source is None:
                    n_ignores += 1
                    continue

                # Determine le contribuable ACTUEL de la parcelle (suit
                # une eventuelle mutation) ; repli sur l'ancien
                # contribuable connu si aucun proprietaire/contribuable
                # actuel n'est identifiable.
                contribuable_id = source.contribuable_id
                if parcelle_id is not None and source.parcelle and source.parcelle.proprietaire_id:
                    contribuable_actuel = (
                        Contribuable.objects
                        .filter(proprietaire_id=source.parcelle.proprietaire_id)
                        .order_by('-date_creation')
                        .first()
                    )
                    if contribuable_actuel is not None and contribuable_actuel.pk != source.contribuable_id:
                        contribuable_id = contribuable_actuel.pk
                        n_mutations_suivies += 1

                deja_emise = Taxation.objects.filter(
                    contribuable_id=contribuable_id,
                    type_taxe_id=type_taxe_id,
                    parcelle_id=parcelle_id,
                    annee_fiscale=annee_cible,
                ).exists()
                if deja_emise:
                    n_deja_present += 1
                    continue

                if parcelle_id is not None:
                    parcelle_exoneree = Parcelle.objects.filter(
                        pk=parcelle_id, statut_fiscal='EXONERE'
                    ).exists()
                    if parcelle_exoneree:
                        n_exonerees += 1
                        continue

                Taxation.objects.create(
                    contribuable_id=contribuable_id,
                    type_taxe_id=type_taxe_id,
                    parcelle_id=parcelle_id,
                    annee_fiscale=annee_cible,
                    montant_du=source.montant_du,
                    simulation_fiscale=source.simulation_fiscale,
                )
                n_crees += 1

        self.stdout.write(self.style.SUCCESS(
            f"Role {annee_cible} emis : {n_crees} nouvelle(s) taxation(s) creee(s), "
            f"{n_deja_present} deja existante(s) (ignorees), "
            f"{n_exonerees} parcelle(s) exoneree(s) (sautees)."
        ))
        if n_mutations_suivies:
            self.stdout.write(self.style.SUCCESS(
                f"{n_mutations_suivies} taxation(s) emise(s) au nom du NOUVEAU proprietaire "
                f"(mutation fiscale suivie)."
            ))
        if n_ignores:
            self.stdout.write(self.style.WARNING(
                f"{n_ignores} combinaison(s) ignoree(s) (taxation source introuvable, cas rare)."
            ))