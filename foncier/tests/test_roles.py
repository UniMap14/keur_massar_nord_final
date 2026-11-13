# ============================================================
# foncier/tests/test_roles.py
#
# Vérifie la séparation Agent fiscal / Agent technique / Superviseur
# mise en place dans foncier/permissions.py.
# ============================================================

from django.test import TestCase
from django.urls import reverse

from foncier.models import DemandeService, MessageInterneMaire, TypeDemande
from foncier.tests.fixtures import (
    creer_agent, creer_citoyen, creer_contribuable, creer_parcelle, creer_taxation,
)


class RolesAccesDashboardTest(TestCase):
    def _login(self, agent):
        self.client.login(username=agent.username, password="motdepasse123")

    def test_agent_fiscal_accede_aux_contribuables(self):
        agent = creer_agent(role="fiscal")
        self._login(agent)
        response = self.client.get(reverse("dashboard_contribuable_list"))
        self.assertEqual(response.status_code, 200)

    def test_taxations_sont_paginees_et_recherchables(self):
        agent = creer_agent(role="fiscal")
        for numero in range(55):
            contribuable = creer_contribuable(
                numero_fiscal=f"CTB-PAGE-{numero:03d}",
                nom=f"Contribuable{numero:03d}",
            )
            creer_taxation(contribuable)

        self._login(agent)
        url = reverse("dashboard_taxation_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["nombre_total"], 55)
        self.assertEqual(len(response.context["objets"]), 50)
        self.assertContains(response, "Page 1 sur 2")
        self.assertContains(response, "Contribuable054")
        self.assertNotContains(response, "Contribuable000")

        response = self.client.get(url, {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["objets"]), 5)
        self.assertContains(response, "Contribuable000")

        response = self.client.get(url, {"q": "CTB-PAGE-054"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["nombre_total"], 1)
        self.assertContains(response, "Contribuable054")

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

    def test_maire_consulte_le_geoportail_sans_acceder_aux_modifications(self):
        maire = creer_agent(role="superviseur")
        self._login(maire)

        response = self.client.get(reverse("geoportail_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "filter-statut")
        self.assertContains(response, "const peutFiscal = true")
        self.assertContains(response, "const peutModifierCadastre = false")
        self.assertNotContains(response, "parcelle_update_fiscal")
        self.assertNotContains(response, "contenuFormulaireEdition")
        self.assertContains(response, 'id="rayonTitle"')
        self.assertContains(response, 'id="rayon-slider"')
        self.assertContains(response, 'id="btnDessinPolygone"')
        self.assertNotContains(response, 'id="selectionTitle"')
        self.assertContains(response, 'id="btnReinitialiserAnalyses"')
        self.assertContains(response, 'id="btnReinitialiserQuartiers"')
        self.assertNotEqual(self.client.get(reverse("admin:index")).status_code, 200)

    def test_maire_ne_peut_pas_creer_ou_modifier_une_parcelle(self):
        maire = creer_agent(role="superviseur")
        parcelle = creer_parcelle()
        self._login(maire)

        response = self.client.get(reverse("dashboard_parcelle_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Statut fiscal")
        self.assertNotContains(response, "Modifier</a>")

        self.assertEqual(
            self.client.get(reverse("dashboard_parcelle_create")).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                reverse("dashboard_parcelle_update", args=[parcelle.pk])
            ).status_code,
            403,
        )
        response = self.client.post(
            reverse("parcelle_update_fiscal", args=[parcelle.pk]),
            {"statut_fiscal": "EN_RETARD"},
        )
        self.assertEqual(response.status_code, 403)
        parcelle.refresh_from_db()
        self.assertNotEqual(parcelle.statut_fiscal, "EN_RETARD")

    def test_maire_consulte_la_fiscalite_en_lecture_seule_et_peut_signaler(self):
        maire = creer_agent(role="superviseur")
        self._login(maire)

        response = self.client.get(reverse("dashboard_contribuable_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Signaler une correction aux chefs")
        self.assertNotContains(response, reverse("dashboard_contribuable_create"))
        self.assertNotContains(response, reverse("dashboard_contribuable_update", args=[1]))
        self.assertNotContains(response, reverse("dashboard_contribuable_delete", args=[1]))

        response = self.client.get(reverse("dashboard_taxation_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("dashboard_taxation_create"))

        response = self.client.get(
            reverse("dashboard_recherche_globale"), {"q": "contribuable"}
        )
        self.assertEqual(response.status_code, 200)

    def test_maire_ne_peut_pas_creer_modifier_ou_supprimer_les_donnees_fiscales(self):
        maire = creer_agent(role="superviseur")
        self._login(maire)

        routes_creation = (
            "dashboard_contribuable_create",
            "dashboard_taxation_create",
            "dashboard_paiement_create",
            "dashboard_typetaxe_create",
        )
        for route in routes_creation:
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 403)

        routes_par_pk = (
            "dashboard_contribuable_update",
            "dashboard_contribuable_delete",
            "dashboard_taxation_update",
            "dashboard_taxation_delete",
            "dashboard_paiement_update",
            "dashboard_paiement_delete",
            "dashboard_typetaxe_update",
            "dashboard_typetaxe_delete",
        )
        for route in routes_par_pk:
            with self.subTest(route=route):
                self.assertEqual(
                    self.client.get(reverse(route, args=[1])).status_code,
                    403,
                )

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

    def test_agent_fiscal_a_un_geoportail_en_lecture_seule_sans_liste_cadastrale(self):
        agent = creer_agent(role="fiscal")
        self._login(agent)
        self.assertEqual(
            self.client.get(reverse("dashboard_parcelle_list")).status_code, 403
        )
        response = self.client.get(reverse("geoportail_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertContains(response, "map-admin")
        self.assertContains(response, "filter-statut")
        self.assertNotContains(response, "parcelle_update_fiscal")
        self.assertNotContains(response, "extrait_cadastral_pdf")
        self.assertNotContains(response, "btnInfraSante")
        self.assertNotContains(response, "btnInfraEducation")
        self.assertContains(response, "Type d'infrastructure")
        self.assertContains(response, "groupeInfraPourCategorie")
        self.assertContains(response, "filter-infra-soustype")
        self.assertContains(response, "mettreAJourVisibiliteReinitialisation")
        self.assertContains(response, "Type de structure de santé")
        self.assertContains(response, "Type d'établissement scolaire")
        self.assertContains(response, "aria-expanded")
        self.assertContains(response, "occupationInfo.aide")

    def test_geoportail_public_propose_les_filtres_infrastructures_et_une_interface_accessible(self):
        response = self.client.get(reverse("geoportail"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertNotContains(response, "btnInfraSante")
        self.assertNotContains(response, "btnInfraEducation")
        self.assertContains(response, "Type d'infrastructure")
        self.assertContains(response, "groupeInfraPourCategorie")
        self.assertContains(response, "filter-infra-soustype")
        self.assertContains(response, "mettreAJourVisibiliteReinitialisation")
        self.assertContains(response, "Type de structure de santé")
        self.assertContains(response, "Type d'établissement scolaire")
        self.assertContains(response, "aria-pressed")
        self.assertContains(response, "geo-panel-body")
        self.assertContains(response, "fp-stat-help")
        self.assertContains(response, 'id="rayonTitle"')
        self.assertContains(response, 'id="rayon-slider"')
        self.assertContains(response, 'id="btnDessinPolygone"')
        self.assertNotContains(response, 'id="selectionTitle"')
        self.assertContains(response, 'id="btnReinitialiserAnalyses"')
        self.assertContains(response, 'id="btnReinitialiserQuartiers"')

    def test_agent_de_service_ne_peut_pas_utiliser_admin_django(self):
        agent = creer_agent(role="technique")
        self._login(agent)
        self.assertNotEqual(self.client.get(reverse("admin:index")).status_code, 200)


class MessagerieMaireTest(TestCase):
    def test_maire_et_chef_peuvent_ouvrir_liste_et_conversation(self):
        maire = creer_agent(username="maire_messagerie_test", role="superviseur")
        chef = creer_agent(username="chef_messagerie_test", role="chef_technique")
        message = MessageInterneMaire.objects.create(
            expediteur=maire,
            destinataire=chef,
            sujet="Suivi du dossier",
            contenu="Merci de faire le point.",
        )

        self.client.force_login(maire)
        response = self.client.get(reverse("dashboard_messages_maire"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Suivi du dossier")
        self.assertTemplateUsed(response, "dashboard/messages_maire.html")
        response = self.client.get(
            reverse("dashboard_message_maire_detail", args=[message.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Merci de faire le point.")
        self.assertTemplateUsed(response, "dashboard/message_maire_detail.html")

        self.client.force_login(chef)
        response = self.client.get(reverse("dashboard_messages_maire"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Suivi du dossier")

    def test_une_reponse_est_rattachee_a_la_conversation(self):
        maire = creer_agent(username="maire_reponse_test", role="superviseur")
        chef = creer_agent(username="chef_reponse_test", role="chef_technique")
        message = MessageInterneMaire.objects.create(
            expediteur=maire,
            destinataire=chef,
            sujet="Question cadastrale",
            contenu="Quel est l'avancement ?",
        )
        self.client.force_login(chef)

        response = self.client.post(
            reverse("dashboard_message_maire_detail", args=[message.pk]),
            {
                "destinataire": maire.pk,
                "sujet": "Re: Question cadastrale",
                "contenu": "Le dossier est en cours de traitement.",
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard_message_maire_detail", args=[message.pk]),
        )
        reponse = MessageInterneMaire.objects.get(parent=message)
        self.assertEqual(reponse.expediteur, chef)
        self.assertEqual(reponse.destinataire, maire)


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
