# ============================================================
# foncier/tests/test_audit.py
#
# Vérifie que le journal d'audit (foncier/audit.py) capture bien les
# créations/modifications, avec le bon utilisateur et le bon détail
# avant/après.
# ============================================================

from django.test import TestCase, RequestFactory

from foncier.middleware import CurrentUserMiddleware
from foncier.models import JournalAudit
from foncier.tests.fixtures import creer_agent, creer_parcelle


class JournalAuditTest(TestCase):
    def setUp(self):
        self.agent = creer_agent(username="agent_audit")

    def _avec_utilisateur_courant(self, fonction):
        """Simule le middleware CurrentUserMiddleware pour que les
        signaux d'audit sachent quel utilisateur est à l'origine du
        changement (normalement rempli par une vraie requête HTTP)."""
        request = RequestFactory().get("/")
        request.user = self.agent
        middleware = CurrentUserMiddleware(lambda r: fonction())
        return middleware(request)

    def test_creation_parcelle_journalisee(self):
        avant = JournalAudit.objects.count()
        self._avec_utilisateur_courant(lambda: creer_parcelle(nicad="AUDIT001"))

        entree = JournalAudit.objects.latest("horodatage")
        self.assertEqual(JournalAudit.objects.count(), avant + 1)
        self.assertEqual(entree.action, "CREATION")
        self.assertEqual(entree.modele, "Parcelle")
        self.assertEqual(entree.utilisateur, self.agent)

    def test_modification_journalisee_avec_avant_apres(self):
        parcelle = creer_parcelle(nicad="AUDIT002", statut_fiscal="A_JOUR")

        def modifier():
            parcelle.statut_fiscal = "EN_RETARD"
            parcelle.save()

        self._avec_utilisateur_courant(modifier)

        entree = JournalAudit.objects.filter(modele="Parcelle", action="MODIFICATION").latest("horodatage")
        self.assertIn("statut_fiscal", entree.champs_modifies)
        self.assertEqual(entree.champs_modifies["statut_fiscal"], ["A_JOUR", "EN_RETARD"])

    def test_modification_sans_champ_suivi_nest_pas_journalisee(self):
        """Modifier un champ qui n'est pas dans TRACKED_MODELS (ex: la
        géométrie) ne doit pas créer d'entrée fantôme dans le journal."""
        parcelle = creer_parcelle(nicad="AUDIT003")
        avant = JournalAudit.objects.filter(modele="Parcelle", action="MODIFICATION").count()

        def resauvegarder_sans_rien_changer():
            parcelle.save()

        self._avec_utilisateur_courant(resauvegarder_sans_rien_changer)

        apres = JournalAudit.objects.filter(modele="Parcelle", action="MODIFICATION").count()
        self.assertEqual(avant, apres)

    def test_journal_audit_reserve_au_superviseur(self):
        agent_fiscal = creer_agent(username="agent_non_superviseur", role="fiscal")
        self.client.login(username=agent_fiscal.username, password="motdepasse123")

        from django.urls import reverse
        response = self.client.get(reverse("dashboard_journal_audit_list"))
        self.assertEqual(response.status_code, 403)
