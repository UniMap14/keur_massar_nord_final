# ============================================================
# foncier/tests/test_roles.py
#
# Vérifie la séparation Agent fiscal / Agent technique / Superviseur
# mise en place dans foncier/permissions.py.
# ============================================================

from django.test import TestCase
from django.urls import reverse

from foncier.tests.fixtures import creer_agent


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
