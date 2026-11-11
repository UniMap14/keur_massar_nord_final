from django.test import TestCase
from django.urls import reverse

from foncier.tests.fixtures import creer_agent, creer_parcelle, creer_proprietaire


class ParcelleProprietaireFormTests(TestCase):
    def setUp(self):
        self.agent = creer_agent(username="agent_cadastre_form", role="technique")
        self.client.force_login(self.agent)
        self.proprietaire = creer_proprietaire(
            nom="Diop", prenom="Awa", ni_cni="1111222233334"
        )
        self.parcelle = creer_parcelle(
            nicad="PARCELLE-OWNER-TEST",
            proprietaire=self.proprietaire,
        )
        self.url = reverse(
            "dashboard_parcelle_update", kwargs={"pk": self.parcelle.pk}
        )

    def _post_data(self, **owner_fields):
        return {
            "nicad": self.parcelle.nicad,
            "proprietaire_nom": "Ba",
            "proprietaire_prenom": "Fatou",
            "proprietaire_ni_cni": "2222333344445",
            "zone": "",
            "superficie": "300",
            "type_document": "DELIB",
            "adresse_parcelle": "",
            "geom": self.parcelle.geom.wkt,
            **owner_fields,
        }

    def test_form_prefills_owner_name_and_cni(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Diop"')
        self.assertContains(response, 'value="Awa"')
        self.assertContains(response, 'value="1111222233334"')

    def test_map_uses_esri_tiles_instead_of_public_osm_tile_server(self):
        response = self.client.get(self.url)

        self.assertContains(
            response,
            "server.arcgisonline.com/ArcGIS/rest/services/World_Imagery",
        )
        self.assertContains(response, "Tiles &copy; Esri")
        self.assertNotContains(response, "tile.openstreetmap.org")

    def test_existing_multipolygon_is_passed_to_map_as_geojson(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "dashboard/widgets/leaflet_polygon.html")
        self.assertContains(response, 'var existingGeoJSON = { "type": "MultiPolygon"')
        self.assertContains(response, "existingLayer.eachLayer(function (l) { drawnItems.addLayer(l); })")

    def test_update_creates_owner_from_entered_name_and_cni(self):
        response = self.client.post(self.url, self._post_data())

        self.assertEqual(response.status_code, 302)
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.proprietaire.nom, "Ba")
        self.assertEqual(self.parcelle.proprietaire.prenom, "Fatou")
        self.assertEqual(self.parcelle.proprietaire.ni_cni, "2222333344445")

    def test_owner_fields_must_be_completed_together(self):
        response = self.client.post(
            self.url,
            self._post_data(proprietaire_ni_cni=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Renseignez ce champ pour enregistrer le propriétaire.")
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.proprietaire, self.proprietaire)
