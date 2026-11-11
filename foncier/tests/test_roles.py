# ============================================================
# foncier/tests/test_roles.py
#
# Vérifie la séparation Agent fiscal / Agent technique / Superviseur
# mise en place dans foncier/permissions.py.
# ============================================================

from django.test import TestCase
from django.urls import reverse

from foncier.models import DemandeService, TypeDemande
from foncier.tests.fixtures import creer_agent, creer_citoyen


class RolesAccesDashboardTest(TestCase):
    def _login(self, agent):
        self.client.login(username=agent.username, password="motdepasse123")

    def test_agent_fiscal_accede_aux_contribuables(self):
        agent = creer_agent(role="fiscal")
        self._login(agent)
        response = self.client.get(reverse("dashboard_contribuable_list"))
        self.assertEqual(response.status_code, 200)

    def test_agent_fiscal_bloque_sur_section_technique(self):
        agent = creer_agent(role="fiscal")
        self._login(agent)
        response = self.client.get(reverse("dashboard_signalement_list"))
        self.assertEqual(response.status_code, 403)

    def test_agent_technique_accede_aux_signalements(self):
        agent = creer_agent(role="technique")
        self._login(agent)
        response = self.client.get(reverse("dashboard_signalement_list"))
        self.assertEqual(response.status_code, 200)

    def test_agent_technique_bloque_sur_section_fiscale(self):
        agent = creer_agent(role="technique")
        self._login(agent)
        response = self.client.get(reverse("dashboard_contribuable_list"))
        self.assertEqual(response.status_code, 403)

    def test_superviseur_accede_a_tout(self):
        agent = creer_agent(role="superviseur")
        self._login(agent)
        self.assertEqual(self.client.get(reverse("dashboard_contribuable_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard_signalement_list")).status_code, 200)

    def test_compte_sans_role_garde_acces_complet(self):
        """Rétrocompatibilité : un compte staff jamais assigné à un rôle
        ne doit jamais se retrouver bloqué (voir foncier/permissions.py)."""
        agent = creer_agent(role=None)
        self._login(agent)
        self.assertEqual(self.client.get(reverse("dashboard_contribuable_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard_signalement_list")).status_code, 200)

    def test_gestion_agents_reservee_au_superviseur(self):
        agent = creer_agent(role="fiscal")
        self._login(agent)
        response = self.client.get(reverse("dashboard_agent_list"))
        self.assertEqual(response.status_code, 403)

    def test_journal_audit_reserve_au_superviseur(self):
        agent = creer_agent(role="technique")
        self._login(agent)
        response = self.client.get(reverse("dashboard_journal_audit_list"))
        self.assertEqual(response.status_code, 403)

    def test_agent_fiscal_bloque_sur_les_parcelles_et_le_geoportail_cadastral(self):
        agent = creer_agent(role="fiscal")
        self._login(agent)
        self.assertEqual(
            self.client.get(reverse("dashboard_parcelle_list")).status_code, 403
        )
        self.assertEqual(self.client.get(reverse("geoportail_admin")).status_code, 403)

    def test_agent_de_service_ne_peut_pas_utiliser_admin_django(self):
        agent = creer_agent(role="technique")
        self._login(agent)
        self.assertNotEqual(self.client.get(reverse("admin:index")).status_code, 200)


class AttributionDemandesTest(TestCase):
    def _login(self, user):
        self.client.force_login(user)

    def _creer_demande(self, categorie):
        demandeur = creer_citoyen(username=f"citoyen_{categorie.lower()}")
        type_demande = TypeDemande.objects.create(
            libelle=f"Démarche {categorie}",
            categorie=categorie,
        )
        return DemandeService.objects.create(
            demandeur=demandeur,
            type_demande=type_demande,
        )

    def test_chef_cadastre_attribue_au_gestionnaire_du_service(self):
        chef = creer_agent(username="chef_cadastre_test", role="chef_technique")
        agent = creer_agent(username="agent_cadastre_test", role="technique")
        demande = self._creer_demande("CADASTRE")

        self._login(chef)
        response = self.client.get(
            reverse("dashboard_demande_detail", args=[demande.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("agent_traitant", response.context["form"].fields)
        self.assertNotIn("statut", response.context["form"].fields)

        response = self.client.post(
            reverse("dashboard_demande_detail", args=[demande.pk]),
            {"agent_traitant": agent.pk},
        )
        self.assertEqual(response.status_code, 302)
        demande.refresh_from_db()
        self.assertEqual(demande.agent_traitant, agent)
        self.assertEqual(demande.statut, DemandeService.STATUT_RECUE)

    def test_chef_fiscal_ne_peut_confier_qu_a_un_agent_fiscal(self):
        chef = creer_agent(username="chef_fiscal_test2", role="chef_fiscal")
        agent_cadastre = creer_agent(username="agent_cadastre_test3", role="technique")
        demande = self._creer_demande("FISCALITE")
        self._login(chef)

        response = self.client.post(
            reverse("dashboard_demande_detail", args=[demande.pk]),
            {"agent_traitant": agent_cadastre.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].has_error("agent_traitant"))
        demande.refresh_from_db()
        self.assertIsNone(demande.agent_traitant)

    def test_agent_ne_voit_et_ne_traite_que_son_dossier(self):
        agent = creer_agent(username="agent_cadastre_test2", role="technique")
        autre_agent = creer_agent(username="autre_cadastre_test", role="technique")
        demande = self._creer_demande("CADASTRE")
        demande.agent_traitant = agent
        demande.save(update_fields=["agent_traitant"])

        self._login(autre_agent)
        self.assertEqual(
            self.client.get(
                reverse("dashboard_demande_detail", args=[demande.pk])
            ).status_code,
            403,
        )

        self._login(agent)
        response = self.client.get(
            reverse("dashboard_demande_detail", args=[demande.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("statut", response.context["form"].fields)
        self.assertNotIn("agent_traitant", response.context["form"].fields)

        dossier_autre = DemandeService.objects.create(
            demandeur=creer_citoyen(username="citoyen_autre_cadastre"),
            type_demande=demande.type_demande,
            agent_traitant=autre_agent,
        )
        response = self.client.get(reverse("dashboard_demande_list"))
        self.assertContains(response, demande.numero_dossier)
        self.assertNotContains(response, dossier_autre.numero_dossier)

        self.client.post(
            reverse("dashboard_demande_detail", args=[demande.pk]),
            {
                "statut": DemandeService.STATUT_EN_COURS,
                "statut_paiement": demande.statut_paiement,
                "commentaire_agent": "",
                "agent_traitant": autre_agent.pk,
            },
        )
        demande.refresh_from_db()
        self.assertEqual(demande.agent_traitant, agent)
        self.assertEqual(demande.statut, DemandeService.STATUT_EN_COURS)

    def test_services_ne_peuvent_pas_voir_les_demandes_de_l_autre(self):
        demande_cadastre = self._creer_demande("CADASTRE")
        demande_fiscale = self._creer_demande("FISCALITE")
        chef_cadastre = creer_agent(username="chef_cadastre_test3", role="chef_technique")
        chef_fiscal = creer_agent(username="chef_fiscal_test", role="chef_fiscal")

        self._login(chef_fiscal)
        self.assertEqual(
            self.client.get(
                reverse("dashboard_demande_detail", args=[demande_cadastre.pk])
            ).status_code,
            403,
        )
        self._login(chef_cadastre)
        self.assertEqual(
            self.client.get(
                reverse("dashboard_demande_detail", args=[demande_fiscale.pk])
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                reverse("demande_piece_jointe", args=[demande_fiscale.pk])
            ).status_code,
            403,
        )
