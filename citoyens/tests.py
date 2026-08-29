# ============================================================
# citoyens/tests.py
#
# Test de sécurité critique : un citoyen connecté ne doit JAMAIS
# pouvoir consulter ou payer la taxation d'un AUTRE citoyen, même en
# devinant/modifiant l'identifiant dans l'URL (/espace/taxations/<id>/payer/).
# ============================================================

from django.test import TestCase
from django.urls import reverse

from foncier.tests.fixtures import creer_contribuable, creer_taxation, creer_citoyen


class SecuritePaiementCitoyenTest(TestCase):
    def setUp(self):
        # Deux contribuables/citoyens distincts, chacun avec sa propre taxation.
        self.contribuable_a = creer_contribuable(numero_fiscal="CTB-A")
        self.contribuable_b = creer_contribuable(numero_fiscal="CTB-B", nom="Ndiaye", prenom="Moussa")

        self.taxation_a = creer_taxation(self.contribuable_a)
        self.taxation_b = creer_taxation(self.contribuable_b)

        self.citoyen_a = creer_citoyen(username="citoyen_a", contribuable=self.contribuable_a)
        self.citoyen_b = creer_citoyen(username="citoyen_b", contribuable=self.contribuable_b)

    def test_citoyen_peut_acceder_a_sa_propre_taxation(self):
        self.client.login(username="citoyen_a", password="motdepasse123")
        response = self.client.get(reverse("citoyen_payer_taxation", args=[self.taxation_a.pk]))
        self.assertEqual(response.status_code, 200)

    def test_citoyen_ne_peut_pas_acceder_a_la_taxation_dun_autre(self):
        """Si ce test échoue, c'est une faille de sécurité grave :
        un citoyen pourrait voir/payer les impôts d'un autre."""
        self.client.login(username="citoyen_a", password="motdepasse123")
        response = self.client.get(reverse("citoyen_payer_taxation", args=[self.taxation_b.pk]))
        self.assertEqual(response.status_code, 404)  # get_object_or_404 filtré par contribuable

    def test_anonyme_redirige_vers_connexion(self):
        response = self.client.get(reverse("citoyen_payer_taxation", args=[self.taxation_a.pk]))
        self.assertNotEqual(response.status_code, 200)

    def test_paiement_en_ligne_confirme_ne_peut_etre_consulte_que_par_son_proprietaire(self):
        from foncier.tests.fixtures import creer_paiement

        paiement = creer_paiement(self.taxation_a, statut='CONFIRME')

        # Le citoyen A voit bien son propre paiement.
        self.client.login(username="citoyen_a", password="motdepasse123")
        response = self.client.get(reverse("citoyen_paiement_retour", args=[paiement.pk]))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Le citoyen B ne doit jamais pouvoir le consulter.
        self.client.login(username="citoyen_b", password="motdepasse123")
        response = self.client.get(reverse("citoyen_paiement_retour", args=[paiement.pk]))
        self.assertEqual(response.status_code, 403)
