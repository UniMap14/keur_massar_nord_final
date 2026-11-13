# ============================================================
# foncier/tests/test_securite_donnees.py
#
# Le tout premier problème corrigé dans ce projet (signalements
# affichés publiquement) était une fuite de confidentialité. Ces
# tests garantissent que ce type de régression ne peut plus jamais
# repasser inaperçu :
#   - le géojson public ne contient JAMAIS de donnée fiscale/propriétaire
#   - le géojson admin est bien réservé aux agents connectés
#   - un signalement n'est consultable que via son code secret
# ============================================================

from django.test import TestCase, Client
from django.urls import reverse

from foncier.models import CategorieInfrastructure, Infrastructure, Signalement
from foncier.tests.fixtures import (
    creer_agent, creer_contribuable, creer_parcelle, creer_proprietaire, creer_taxation,
)


class ApiParcellesPubliqueTest(TestCase):
    def setUp(self):
        self.proprietaire = creer_proprietaire()
        self.parcelle = creer_parcelle(
            nicad="TESTPUB01",
            statut_fiscal="EN_RETARD",
            montant_taxe_annuelle=123456,
            valeur_locative=99999,
            proprietaire=self.proprietaire,
        )

    def test_geojson_public_ne_contient_aucune_donnee_fiscale(self):
        # bbox couvrant la géométrie de test (voir fixtures.creer_geometrie_carree).
        response = self.client.get(reverse("api_parcelles") + "?bbox=-17.32,14.78,-17.30,14.80")
        self.assertEqual(response.status_code, 200)

        contenu = response.json()
        self.assertTrue(contenu["features"], "Aucune parcelle renvoyée : la bbox ne couvre pas la géométrie de test.")
        proprietes = contenu["features"][0]["properties"]

        # Champs qui NE DOIVENT JAMAIS apparaître côté public.
        for champ_interdit in (
            "statut_fiscal", "montant_taxe_annuelle", "valeur_locative",
            "proprietaire", "proprietaire_nom", "proprietaire_prenom", "proprietaire_cni",
        ):
            self.assertNotIn(
                champ_interdit, proprietes,
                f"FUITE DE DONNÉES : le champ '{champ_interdit}' ne doit jamais être exposé publiquement.",
            )

        # Champs qui DOIVENT être là (l'info publique légitime).
        self.assertIn("nicad", proprietes)
        self.assertIn("superficie", proprietes)

    def test_geojson_admin_inaccessible_sans_connexion(self):
        response = self.client.get(reverse("api_parcelles_admin") + "?bbox=-17.32,14.78,-17.30,14.80")
        # Redirection vers la connexion, jamais un accès direct aux données.
        self.assertNotEqual(response.status_code, 200)

    def test_geojson_admin_accessible_a_un_agent_connecte(self):
        agent = creer_agent()
        self.client.login(username=agent.username, password="motdepasse123")

        response = self.client.get(reverse("api_parcelles_admin") + "?bbox=-17.32,14.78,-17.30,14.80")
        self.assertEqual(response.status_code, 200)

        contenu = response.json()
        self.assertTrue(contenu["features"], "Aucune parcelle renvoyée : la bbox ne couvre pas la géométrie de test.")
        proprietes = contenu["features"][0]["properties"]
        self.assertIn("statut_fiscal", proprietes)
        self.assertIn("proprietaire", proprietes)
        self.assertEqual(proprietes["proprietaire_nom"], self.proprietaire.nom)
        self.assertEqual(proprietes["proprietaire_prenom"], self.proprietaire.prenom)
        self.assertEqual(proprietes["proprietaire_cni"], self.proprietaire.ni_cni)

    def test_geojson_admin_cadastre_ne_contient_aucune_donnee_fiscale(self):
        agent = creer_agent(role="technique")
        self.client.force_login(agent)

        for route in ("api_parcelles_admin", "api_parcelles_toutes_admin"):
            response = self.client.get(
                reverse(route) + "?bbox=-17.32,14.78,-17.30,14.80"
            )
            self.assertEqual(response.status_code, 200)
            properties = response.json()["features"][0]["properties"]
            self.assertEqual(properties["proprietaire_nom"], self.proprietaire.nom)
            self.assertEqual(properties["proprietaire_prenom"], self.proprietaire.prenom)
            self.assertEqual(properties["proprietaire_cni"], self.proprietaire.ni_cni)
            for champ_interdit in (
                "statut_fiscal",
                "montant_taxe_annuelle",
                "valeur_locative",
                "simulation_fiscale",
            ):
                self.assertNotIn(champ_interdit, properties)

    def test_geoportail_admin_affiche_et_edite_les_champs_du_proprietaire(self):
        agent = creer_agent(role="technique")
        self.client.force_login(agent)

        response = self.client.get(reverse("geoportail_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nom du propriétaire")
        self.assertContains(response, "Prénom du propriétaire")
        self.assertContains(response, "N° CNI")
        self.assertContains(response, "Adresse / secteur")
        self.assertContains(response, "ep-adresse")
        self.assertContains(response, "proprietaire_cni")
        self.assertContains(response, "proprietaire_nom")
        self.assertContains(response, "p.proprietaire_nom ||")
        self.assertContains(response, "p.proprietaire_cni ||")

    def test_superviseur_voit_proprietaires_et_statuts_fiscaux_sur_toutes_les_parcelles(self):
        agent = creer_agent(role="superviseur")
        self.client.force_login(agent)

        page = self.client.get(reverse("geoportail_admin"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Nom du propriétaire")
        self.assertContains(page, "N° CNI")
        self.assertContains(page, "Statut fiscal")
        self.assertContains(page, "filter-statut")

        response = self.client.get(reverse("api_parcelles_toutes_admin"))
        self.assertEqual(response.status_code, 200)
        properties = response.json()["features"][0]["properties"]
        self.assertEqual(properties["proprietaire_nom"], self.proprietaire.nom)
        self.assertEqual(properties["proprietaire_prenom"], self.proprietaire.prenom)
        self.assertEqual(properties["proprietaire_cni"], self.proprietaire.ni_cni)
        self.assertEqual(properties["statut_fiscal"], "EN_RETARD")

    def test_agent_cadastre_peut_renseigner_le_proprietaire_depuis_la_carte(self):
        agent = creer_agent(role="technique")
        self.client.force_login(agent)

        response = self.client.post(
            reverse("parcelle_update_fiscal", kwargs={"parcelle_id": self.parcelle.pk}),
            {
                "proprietaire_nom": "Ndiaye",
                "proprietaire_prenom": "Moussa",
                "proprietaire_cni": "9876543210123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["proprietaire_nom"], "Ndiaye")
        self.assertEqual(response.json()["proprietaire_prenom"], "Moussa")
        self.assertEqual(response.json()["proprietaire_cni"], "9876543210123")
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.proprietaire.nom, "Ndiaye")

    def test_agent_cadastre_ne_peut_pas_soumettre_un_proprietaire_incomplet(self):
        agent = creer_agent(role="technique")
        self.client.force_login(agent)

        response = self.client.post(
            reverse("parcelle_update_fiscal", kwargs={"parcelle_id": self.parcelle.pk}),
            {"proprietaire_nom": "Ndiaye", "proprietaire_prenom": "", "proprietaire_cni": ""},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Renseignez le nom", response.json()["error"])
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.proprietaire, self.proprietaire)

    def test_liste_cadastrale_ne_montre_pas_les_donnees_fiscales(self):
        agent = creer_agent(role="technique")
        self.client.force_login(agent)

        response = self.client.get(reverse("dashboard_parcelle_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Statut fiscal")
        self.assertNotContains(response, "Taxe annuelle")
        self.assertNotContains(response, "En retard")

    def test_agent_fiscal_voit_toutes_les_parcelles_actives_et_les_infrastructures(self):
        agent = creer_agent(role="fiscal")
        self.client.force_login(agent)
        contribuable = creer_contribuable(numero_fiscal="CTB-GEO-FISCAL")
        taxation = creer_taxation(contribuable, parcelle=self.parcelle)
        parcelle_non_taxee = creer_parcelle(nicad="TESTNONFISCAL01")
        creer_parcelle(nicad="TESTINACTIVE01", parcelle_active=False)
        categorie = CategorieInfrastructure.objects.create(
            code="ecole-test",
            label="Écoles",
            icone="fa-school",
            couleur="#3468a8",
        )
        Infrastructure.objects.create(
            categorie=categorie,
            nom="École de test",
            parcelle=self.parcelle,
            latitude=14.79,
            longitude=-17.31,
            details={"Horaires": "8 h - 17 h", "Nombre d'employés": 12},
        )
        Infrastructure.objects.create(
            categorie=categorie,
            nom="Forage hors parcelle",
            latitude=14.791,
            longitude=-17.309,
        )

        page = self.client.get(reverse("geoportail_admin"))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "foncier/geoportail_admin.html")
        self.assertContains(page, "map-admin")
        self.assertContains(page, "filter-statut")
        self.assertContains(page, "Statut fiscal")
        self.assertContains(page, "World_Street_Map/MapServer/tile")
        self.assertNotContains(page, "tile.openstreetmap.org")
        self.assertNotContains(page, "parcelle_update_fiscal")
        self.assertNotContains(page, "extrait_cadastral_pdf")
        self.assertNotContains(page, "Nom du propriétaire")
        self.assertNotContains(page, "N° CNI")
        self.assertNotContains(page, self.proprietaire.ni_cni)

        for route in ("api_parcelles_admin", "api_parcelles_toutes_admin"):
            url = reverse(route)
            if route == "api_parcelles_admin":
                url += "?bbox=-17.32,14.78,-17.30,14.80"
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data["features"]), 2)
            properties_by_id = {
                feature["properties"]["id"]: feature["properties"]
                for feature in data["features"]
            }
            properties = properties_by_id[self.parcelle.pk]
            self.assertIn("statut_fiscal", properties)
            self.assertIn("montant_taxe_annuelle", properties)
            self.assertEqual(properties_by_id[parcelle_non_taxee.pk]["infrastructures"], [])
            self.assertEqual(properties["infrastructures"][0]["nom"], "École de test")
            self.assertNotIn("id", properties["infrastructures"][0])
            self.assertNotIn("Nombre d'employés", properties["infrastructures"][0]["details"])
            if route == "api_parcelles_toutes_admin":
                self.assertEqual(data["infrastructures_hors_parcelle"][0]["nom"], "Forage hors parcelle")
            for champ_interdit in (
                "nicad",
                "adresse_parcelle",
                "zone_nom",
                "type_document",
                "proprietaire_nom",
                "proprietaire_prenom",
                "proprietaire_cni",
            ):
                self.assertNotIn(champ_interdit, properties)

        taxation.delete()
        response = self.client.get(reverse("api_parcelles_toutes_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["features"]), 2)

    def test_ajout_infrastructure_invalide_le_cache_du_geoportail_fiscal(self):
        agent = creer_agent(role="fiscal")
        self.client.force_login(agent)
        url = reverse("api_parcelles_toutes_admin")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        properties = next(
            feature["properties"]
            for feature in response.json()["features"]
            if feature["properties"]["id"] == self.parcelle.pk
        )
        self.assertEqual(properties["infrastructures"], [])

        categorie = CategorieInfrastructure.objects.create(
            code="sante-test",
            label="Santé",
        )
        Infrastructure.objects.create(
            categorie=categorie,
            nom="Poste de santé",
            parcelle=self.parcelle,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        properties = next(
            feature["properties"]
            for feature in response.json()["features"]
            if feature["properties"]["id"] == self.parcelle.pk
        )
        self.assertEqual(properties["infrastructures"][0]["nom"], "Poste de santé")

    def test_agent_fiscal_ne_peut_pas_modifier_les_champs_cadastraux_depuis_le_geoportail(self):
        agent = creer_agent(role="fiscal")
        self.client.force_login(agent)

        response = self.client.post(
            reverse("parcelle_update_fiscal", kwargs={"parcelle_id": self.parcelle.pk}),
            {"nicad": "NICAD-MODIFIE"},
        )

        self.assertEqual(response.status_code, 403)
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.nicad, "TESTPUB01")


class SignalementConfidentialiteTest(TestCase):
    def setUp(self):
        # Titre volontairement différent de l'exemple déjà présent en
        # placeholder dans le formulaire ("Ex : Dépôt d'ordures...") —
        # sinon le test se déclencherait sur cet exemple, pas sur une
        # vraie fuite de données. Pas d'apostrophe non plus : Django
        # échappe ' en &#x27; dans le HTML, ce qui casse une comparaison
        # de texte brut.
        self.signalement = Signalement.objects.create(
            titre="Poteau electrique casse", lieu="Secteur test 42", description="Test",
        )

    def test_signalement_non_liste_publiquement(self):
        """La page d'accueil et /signalement/ ne doivent plus jamais
        lister les signalements des autres citoyens (bug d'origine de ce projet)."""
        response = self.client.get(reverse("signalement"))
        self.assertNotContains(response, self.signalement.titre)
        self.assertNotContains(response, self.signalement.lieu)

    def test_suivi_par_code_secret_fonctionne(self):
        url = reverse("signalement_suivi") + f"?reference={self.signalement.reference}"
        response = self.client.get(url)
        self.assertContains(response, self.signalement.titre)

    def test_suivi_sans_code_ne_revele_aucun_signalement(self):
        response = self.client.get(reverse("signalement_suivi"))
        self.assertNotContains(response, self.signalement.titre)

    def test_code_invalide_ne_plante_pas(self):
        url = reverse("signalement_suivi") + "?reference=ceci-nest-pas-un-uuid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.signalement.titre)
