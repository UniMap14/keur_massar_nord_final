import json

from django.test import RequestFactory, SimpleTestCase

from foncier.forms import SimulateurFiscalForm
from foncier.views import simuler_fiscalite


class SimulateurFoncierTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def simuler(self, **data):
        response = simuler_fiscalite(self.factory.post("/fiscalite/simuler/", data))
        return response.status_code, json.loads(response.content)

    def test_le_formulaire_ne_propose_que_les_quatre_impositions_foncieres(self):
        self.assertEqual(
            [value for value, _label in SimulateurFiscalForm.TYPE_CHOICES],
            ["cfpb", "cfpnb", "irf", "teom"],
        )

    def test_cfpnb_est_calcule_sur_la_valeur_venale_du_terrain_nu(self):
        status, result = self.simuler(
            type_simulation="cfpnb",
            revenu="100000",
            cfpnb_nature="terrain_nu",
        )

        self.assertEqual(status, 200)
        self.assertEqual(result["valeur_venale"], 100000)
        self.assertEqual(result["impot"], 7000)

    def test_cfpb_conserve_le_calcul_existant(self):
        status, result = self.simuler(
            type_simulation="cfpb",
            revenu="1000000",
            cfpb_residence_principale="on",
        )

        self.assertEqual(status, 200)
        self.assertEqual(result["impot"], 25000)

    def test_irf_utilise_le_taux_saisi(self):
        status, result = self.simuler(
            type_simulation="irf",
            revenu="120000",
            taux_irf="10",
        )

        self.assertEqual(status, 200)
        self.assertEqual(result["impot"], 12000)

    def test_teom_utilise_le_taux_saisi(self):
        status, result = self.simuler(
            type_simulation="teom",
            revenu="120000",
            taux_teom="5",
        )

        self.assertEqual(status, 200)
        self.assertEqual(result["impot"], 6000)

    def test_irf_refuse_un_taux_manquant(self):
        status, result = self.simuler(type_simulation="irf", revenu="120000")

        self.assertEqual(status, 400)
        self.assertFalse(result["ok"])

    def test_ancien_type_national_n_est_plus_accepte(self):
        status, result = self.simuler(type_simulation="is", revenu="120000")

        self.assertEqual(status, 400)
        self.assertFalse(result["ok"])
