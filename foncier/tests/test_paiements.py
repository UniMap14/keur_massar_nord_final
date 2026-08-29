# ============================================================
# foncier/tests/test_paiements.py
#
# Un paiement en ligne (Orange Money/Wave) reste "EN_ATTENTE" jusqu'à
# confirmation par l'opérateur. Ces tests garantissent qu'un paiement
# non confirmé ne peut JAMAIS être compté comme réglé, ni donner droit
# à un reçu — sans quoi un citoyen pourrait se croire à jour sans avoir
# vraiment payé.
# ============================================================

from decimal import Decimal

from django.test import TestCase

from foncier.tests.fixtures import creer_contribuable, creer_taxation, creer_paiement


class SoldeTaxationTest(TestCase):
    def setUp(self):
        self.contribuable = creer_contribuable()
        self.taxation = creer_taxation(self.contribuable, montant_du=Decimal("50000.00"))

    def test_solde_initial_egal_au_montant_du(self):
        self.assertEqual(self.taxation.solde, Decimal("50000.00"))

    def test_paiement_confirme_reduit_le_solde(self):
        creer_paiement(self.taxation, montant=Decimal("50000.00"), statut='CONFIRME')
        self.assertEqual(self.taxation.solde, Decimal("0.00"))

    def test_paiement_en_attente_ne_reduit_pas_le_solde(self):
        """Cœur du système de paiement en ligne : tant que l'opérateur
        n'a pas confirmé, le citoyen reste redevable."""
        creer_paiement(self.taxation, montant=Decimal("50000.00"), statut='EN_ATTENTE')
        self.assertEqual(self.taxation.solde, Decimal("50000.00"))

    def test_paiement_echoue_ne_reduit_pas_le_solde(self):
        creer_paiement(self.taxation, montant=Decimal("50000.00"), statut='ECHEC')
        self.assertEqual(self.taxation.solde, Decimal("50000.00"))

    def test_paiement_partiel(self):
        creer_paiement(self.taxation, montant=Decimal("20000.00"), statut='CONFIRME')
        self.assertEqual(self.taxation.solde, Decimal("30000.00"))


class MontantPayeContribuableTest(TestCase):
    def test_montant_paye_total_ignore_les_paiements_non_confirmes(self):
        contribuable = creer_contribuable()
        taxation1 = creer_taxation(contribuable, montant_du=Decimal("10000.00"), annee=2025)
        taxation2 = creer_taxation(contribuable, montant_du=Decimal("20000.00"), annee=2026)

        creer_paiement(taxation1, montant=Decimal("10000.00"), statut='CONFIRME')
        creer_paiement(taxation2, montant=Decimal("20000.00"), statut='EN_ATTENTE')

        self.assertEqual(contribuable.montant_paye_total, Decimal("10000.00"))
        self.assertEqual(contribuable.montant_du_total, Decimal("30000.00"))
        self.assertEqual(contribuable.solde_total, Decimal("20000.00"))
        self.assertEqual(contribuable.statut_global, "EN_RETARD")

    def test_contribuable_a_jour_quand_tout_est_confirme(self):
        contribuable = creer_contribuable()
        taxation = creer_taxation(contribuable, montant_du=Decimal("15000.00"))
        creer_paiement(taxation, montant=Decimal("15000.00"), statut='CONFIRME')

        self.assertEqual(contribuable.statut_global, "A_JOUR")
