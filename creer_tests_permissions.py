# -*- coding: utf-8 -*-
"""
Cree foncier/tests_permissions.py : suite de tests automatises couvrant
les 3 corrections prioritaires de separation des roles/permissions.

Script de creation (pas un patch) : n'ecrit le fichier que s'il n'existe
pas encore, pour ne jamais ecraser silencieusement un fichier de tests
que vous auriez deja.
"""
import os

CHEMIN = "foncier/tests_permissions.py"

CONTENU = '''# -*- coding: utf-8 -*-
"""
Tests automatises pour la separation des roles/permissions (cahier des
charges "SEPARATION DES ROLES, DES RESPONSABILITES ET DES PERMISSIONS").

Couvre les 3 corrections prioritaires appliquees :
  1. parcelle_update_fiscal : controle de role par groupe de champs
     (cadastral -> role technique, fiscal -> role fiscal).
  2. dashboard_morcellement_fusion_list : role \\'technique\\' requis.
  3. dashboard_home : peut_fiscal / peut_technique correctement calcules
     et transmis au template selon le role de l\\'utilisateur connecte.

Execution : python manage.py test foncier.tests_permissions
"""
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.test import TestCase
from django.urls import reverse

from .models import Parcelle, Propriétaire
from .permissions import (
    GROUPE_SUPERVISEUR,
    GROUPE_CHEF_TECHNIQUE,
    GROUPE_GESTIONNAIRE_TECHNIQUE,
    GROUPE_CHEF_FISCAL,
    GROUPE_GESTIONNAIRE_FISCAL,
)


def _geom_test():
    poly = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
    return MultiPolygon(poly)


class BasePermissionsTestCase(TestCase):
    """Cree les 5 groupes de roles + un compte par role + une parcelle de test."""

    @classmethod
    def setUpTestData(cls):
        cls.groupe_superviseur = Group.objects.create(name=GROUPE_SUPERVISEUR)
        cls.groupe_chef_technique = Group.objects.create(name=GROUPE_CHEF_TECHNIQUE)
        cls.groupe_gestionnaire_technique = Group.objects.create(name=GROUPE_GESTIONNAIRE_TECHNIQUE)
        cls.groupe_chef_fiscal = Group.objects.create(name=GROUPE_CHEF_FISCAL)
        cls.groupe_gestionnaire_fiscal = Group.objects.create(name=GROUPE_GESTIONNAIRE_FISCAL)

        def _creer_agent(username, groupe=None):
            user = User.objects.create_user(username=username, password="test1234", is_staff=True)
            if groupe is not None:
                user.groups.add(groupe)
            return user

        cls.superviseur = _creer_agent("test_superviseur", cls.groupe_superviseur)
        cls.chef_technique = _creer_agent("test_chef_technique", cls.groupe_chef_technique)
        cls.gestionnaire_technique = _creer_agent("test_gestionnaire_technique", cls.groupe_gestionnaire_technique)
        cls.chef_fiscal = _creer_agent("test_chef_fiscal", cls.groupe_chef_fiscal)
        cls.gestionnaire_fiscal = _creer_agent("test_gestionnaire_fiscal", cls.groupe_gestionnaire_fiscal)
        cls.staff_sans_groupe = _creer_agent("test_staff_sans_groupe", None)
        cls.non_staff = User.objects.create_user(username="test_non_staff", password="test1234", is_staff=False)

        cls.proprietaire = Propriétaire.objects.create(
            nom="Fall", prenom="Awa", ni_cni="TEST-CNI-0001"
        )
        cls.parcelle = Parcelle.objects.create(
            nicad="TEST-NICAD-0001",
            proprietaire=cls.proprietaire,
            superficie=250.0,
            geom=_geom_test(),
        )


class ParcelleUpdateFiscalRoleSeparationTests(BasePermissionsTestCase):
    """Priorite 1 : verifie que les champs cadastraux et fiscaux de
    parcelle_update_fiscal sont bien cloisonnes par role."""

    def _url(self):
        return reverse("parcelle_update_fiscal", args=[self.parcelle.id])

    def test_gestionnaire_fiscal_peut_modifier_champ_fiscal(self):
        self.client.login(username="test_gestionnaire_fiscal", password="test1234")
        response = self.client.post(self._url(), {"statut_fiscal": "EXONERE"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.statut_fiscal, "EXONERE")

    def test_gestionnaire_fiscal_ne_peut_pas_modifier_champ_cadastral(self):
        self.client.login(username="test_gestionnaire_fiscal", password="test1234")
        response = self.client.post(self._url(), {"nicad": "HACK-0001"})
        self.assertEqual(response.status_code, 403)
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.nicad, "TEST-NICAD-0001")

    def test_gestionnaire_technique_peut_modifier_champ_cadastral(self):
        self.client.login(username="test_gestionnaire_technique", password="test1234")
        response = self.client.post(self._url(), {"nicad": "NOUVEAU-NICAD"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.nicad, "NOUVEAU-NICAD")

    def test_gestionnaire_technique_ne_peut_pas_modifier_champ_fiscal(self):
        self.client.login(username="test_gestionnaire_technique", password="test1234")
        response = self.client.post(self._url(), {"statut_fiscal": "EXONERE"})
        self.assertEqual(response.status_code, 403)
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.statut_fiscal, "A_JOUR")

    def test_superviseur_peut_modifier_les_deux_en_un_seul_appel(self):
        self.client.login(username="test_superviseur", password="test1234")
        response = self.client.post(self._url(), {"nicad": "SUPERVISEUR-NICAD", "statut_fiscal": "EXONERE"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.nicad, "SUPERVISEUR-NICAD")
        self.assertEqual(self.parcelle.statut_fiscal, "EXONERE")

    def test_staff_sans_groupe_garde_acces_complet_retrocompatibilite(self):
        self.client.login(username="test_staff_sans_groupe", password="test1234")
        response = self.client.post(self._url(), {"nicad": "RETROCOMPAT-NICAD", "statut_fiscal": "EXONERE"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

    def test_non_staff_est_redirige_vers_la_connexion(self):
        self.client.login(username="test_non_staff", password="test1234")
        response = self.client.post(self._url(), {"nicad": "INTRUS"})
        self.assertEqual(response.status_code, 302)
        self.parcelle.refresh_from_db()
        self.assertEqual(self.parcelle.nicad, "TEST-NICAD-0001")


class MorcellementFusionListRoleTests(BasePermissionsTestCase):
    """Priorite 2 : seul le service technique (Chef/Gestionnaire Cadastre,
    Superviseur) doit pouvoir consulter la liste morcellement/fusion."""

    def _url(self):
        return reverse("dashboard_morcellement_fusion_list")

    def test_chef_technique_a_acces(self):
        self.client.login(username="test_chef_technique", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_gestionnaire_technique_a_acces(self):
        self.client.login(username="test_gestionnaire_technique", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_superviseur_a_acces(self):
        self.client.login(username="test_superviseur", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_chef_fiscal_est_refuse(self):
        self.client.login(username="test_chef_fiscal", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 403)

    def test_gestionnaire_fiscal_est_refuse(self):
        self.client.login(username="test_gestionnaire_fiscal", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 403)


class DashboardHomeRoleContextTests(BasePermissionsTestCase):
    """Priorite 3 : peut_fiscal / peut_technique correctement calcules
    selon le role de l\\'utilisateur connecte."""

    def _url(self):
        return reverse("dashboard_home")

    def test_superviseur_voit_les_deux_services(self):
        self.client.login(username="test_superviseur", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["peut_fiscal"])
        self.assertTrue(response.context["peut_technique"])

    def test_chef_fiscal_ne_voit_que_le_service_fiscal(self):
        self.client.login(username="test_chef_fiscal", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["peut_fiscal"])
        self.assertFalse(response.context["peut_technique"])

    def test_gestionnaire_technique_ne_voit_que_le_service_technique(self):
        self.client.login(username="test_gestionnaire_technique", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["peut_fiscal"])
        self.assertTrue(response.context["peut_technique"])

    def test_staff_sans_groupe_voit_les_deux_services(self):
        self.client.login(username="test_staff_sans_groupe", password="test1234")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["peut_fiscal"])
        self.assertTrue(response.context["peut_technique"])
'''

if os.path.exists(CHEMIN):
    print(f"ATTENTION : {CHEMIN} existe deja. Rien n'a ete ecrit pour eviter d'ecraser un fichier existant.")
    print("Si vous voulez le remplacer, supprimez-le d'abord ou dites-le-moi.")
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(CONTENU)
    print(f"OK : {CHEMIN} cree.")