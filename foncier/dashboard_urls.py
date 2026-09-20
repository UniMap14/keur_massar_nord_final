# ============================================================
# foncier/dashboard_urls.py
#
# À inclure dans kmsn/urls.py (racine du projet) avec :
#
#   path('gestion/', include('foncier.dashboard_urls')),
#
# Le dashboard custom vivra sur /gestion/, séparé de /admin/
# (admin Django standard, toujours disponible) et de
# /geoportail/ (site public existant).
# ============================================================

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import dashboard_views as views

urlpatterns = [
    path("login/", views.DashboardLoginView.as_view(), name="dashboard_login"),
    path("logout/", LogoutView.as_view(next_page="dashboard_login"), name="dashboard_logout"),

    # --- Mot de passe oublié (4 étapes) ---
    path(
        "mot-de-passe-oublie/",
        views.DashboardPasswordResetView.as_view(),
        name="dashboard_password_reset",
    ),
    path(
        "mot-de-passe-oublie/envoye/",
        views.DashboardPasswordResetDoneView.as_view(),
        name="dashboard_password_reset_done",
    ),
    path(
        "reinitialiser/<uidb64>/<token>/",
        views.DashboardPasswordResetConfirmView.as_view(),
        name="dashboard_password_reset_confirm",
    ),
    path(
        "reinitialiser/termine/",
        views.DashboardPasswordResetCompleteView.as_view(),
        name="dashboard_password_reset_complete",
    ),

    path("", views.dashboard_home, name="dashboard_home"),

    # --- Parcelles (CRUD complet) ---
    path("parcelles/", views.dashboard_parcelle_list, name="dashboard_parcelle_list"),
    path("parcelles/nouvelle/", views.dashboard_parcelle_create, name="dashboard_parcelle_create"),
    path("parcelles/<int:pk>/modifier/", views.dashboard_parcelle_update, name="dashboard_parcelle_update"),
    path("parcelles/<int:pk>/supprimer/", views.dashboard_parcelle_delete, name="dashboard_parcelle_delete"),

    # --- Catégories d'infrastructure (CRUD complet) ---
    path("infrastructures/categories/", views.dashboard_categorie_list, name="dashboard_categorie_list"),
    path("infrastructures/categories/nouvelle/", views.dashboard_categorie_create, name="dashboard_categorie_create"),
    path("infrastructures/categories/<int:pk>/modifier/", views.dashboard_categorie_update, name="dashboard_categorie_update"),
    path("infrastructures/categories/<int:pk>/supprimer/", views.dashboard_categorie_delete, name="dashboard_categorie_delete"),

    # --- Infrastructures (CRUD complet) ---
    path("infrastructures/", views.dashboard_infrastructure_list, name="dashboard_infrastructure_list"),
    path("infrastructures/nouvelle/", views.dashboard_infrastructure_create, name="dashboard_infrastructure_create"),
    path("infrastructures/<int:pk>/modifier/", views.dashboard_infrastructure_update, name="dashboard_infrastructure_update"),
    path("infrastructures/<int:pk>/supprimer/", views.dashboard_infrastructure_delete, name="dashboard_infrastructure_delete"),

    # --- Actualités (CRUD complet) ---
    path("actualites/", views.dashboard_actualite_list, name="dashboard_actualite_list"),
    path("actualites/nouvelle/", views.dashboard_actualite_create, name="dashboard_actualite_create"),
    path("actualites/<int:pk>/modifier/", views.dashboard_actualite_update, name="dashboard_actualite_update"),
    path("actualites/<int:pk>/supprimer/", views.dashboard_actualite_delete, name="dashboard_actualite_delete"),

    # --- Propriétaires (CRUD complet) ---
    path("proprietaires/", views.dashboard_proprietaire_list, name="dashboard_proprietaire_list"),
    path("proprietaires/nouveau/", views.dashboard_proprietaire_create, name="dashboard_proprietaire_create"),
    path("proprietaires/<int:pk>/modifier/", views.dashboard_proprietaire_update, name="dashboard_proprietaire_update"),
    path("proprietaires/<int:pk>/supprimer/", views.dashboard_proprietaire_delete, name="dashboard_proprietaire_delete"),

    # --- Zones (renommer/supprimer seulement — géométrie importée via shapefile) ---
    path("zones/", views.dashboard_zone_list, name="dashboard_zone_list"),
    path("zones/<int:pk>/modifier/", views.dashboard_zone_update, name="dashboard_zone_update"),
    path("zones/<int:pk>/supprimer/", views.dashboard_zone_delete, name="dashboard_zone_delete"),

    # --- Contribuables (CRUD complet) ---
    path("contribuables/", views.dashboard_contribuable_list, name="dashboard_contribuable_list"),
    path("contribuables/export.csv", views.dashboard_contribuable_export_csv, name="dashboard_contribuable_export_csv"),
    path("contribuables/nouveau/", views.dashboard_contribuable_create, name="dashboard_contribuable_create"),
    path("contribuables/<int:pk>/modifier/", views.dashboard_contribuable_update, name="dashboard_contribuable_update"),
    path("contribuables/<int:pk>/supprimer/", views.dashboard_contribuable_delete, name="dashboard_contribuable_delete"),

    # --- Taxations (CRUD complet) ---
    path("declarations/", views.dashboard_declaration_list, name="dashboard_declaration_list"),
        # --- Recours fiscaux (contestations et redressements) ---
    path("recours/", views.dashboard_recours_list, name="dashboard_recours_list"),
        # --- Premières immatriculations fiscales ---
    path("immatriculations/", views.dashboard_immatriculation_list, name="dashboard_immatriculation_list"),
        # --- Exonérations fiscales ---
    path("exonerations/", views.dashboard_exoneration_list, name="dashboard_exoneration_list"),
        # --- Plans de paiement ---
    path("plans-paiement/", views.dashboard_plan_paiement_list, name="dashboard_plan_paiement_list"),
        # --- Mutations fiscales ---
    path("mutations/", views.dashboard_mutation_list, name="dashboard_mutation_list"),
    path("mutations/<int:pk>/traiter/", views.dashboard_mutation_traiter, name="dashboard_mutation_traiter"),
    path("plans-paiement/<int:pk>/traiter/", views.dashboard_plan_paiement_traiter, name="dashboard_plan_paiement_traiter"),
    path("exonerations/<int:pk>/traiter/", views.dashboard_exoneration_traiter, name="dashboard_exoneration_traiter"),
    path("immatriculations/<int:pk>/traiter/", views.dashboard_immatriculation_traiter, name="dashboard_immatriculation_traiter"),
    path("recours/<int:pk>/traiter/", views.dashboard_recours_traiter, name="dashboard_recours_traiter"),
    path("declarations/<int:pk>/traiter/", views.dashboard_declaration_traiter, name="dashboard_declaration_traiter"),
    path("taxations/", views.dashboard_taxation_list, name="dashboard_taxation_list"),
    path("taxations/export.csv", views.dashboard_taxation_export_csv, name="dashboard_taxation_export_csv"),
    path("taxations/nouvelle/", views.dashboard_taxation_create, name="dashboard_taxation_create"),
    path("taxations/<int:pk>/modifier/", views.dashboard_taxation_update, name="dashboard_taxation_update"),
    path("taxations/<int:pk>/supprimer/", views.dashboard_taxation_delete, name="dashboard_taxation_delete"),

    # --- Paiements (CRUD complet) ---
    path("paiements/", views.dashboard_paiement_list, name="dashboard_paiement_list"),
    path("paiements/export.csv", views.dashboard_paiement_export_csv, name="dashboard_paiement_export_csv"),
    path("paiements/nouveau/", views.dashboard_paiement_create, name="dashboard_paiement_create"),
    path("paiements/<int:pk>/modifier/", views.dashboard_paiement_update, name="dashboard_paiement_update"),
    path("paiements/<int:pk>/supprimer/", views.dashboard_paiement_delete, name="dashboard_paiement_delete"),
    path("paiements/<int:pk>/valider/", views.dashboard_paiement_valider, name="dashboard_paiement_valider"),

    # --- Types de taxe (CRUD complet) ---
    path("types-taxe/", views.dashboard_typetaxe_list, name="dashboard_typetaxe_list"),
    path("types-taxe/nouveau/", views.dashboard_typetaxe_create, name="dashboard_typetaxe_create"),
    path("types-taxe/<int:pk>/modifier/", views.dashboard_typetaxe_update, name="dashboard_typetaxe_update"),
    path("types-taxe/<int:pk>/supprimer/", views.dashboard_typetaxe_delete, name="dashboard_typetaxe_delete"),

    # --- Profils citoyens (CRUD complet — lier un compte à un contribuable) ---
    path("profils/", views.dashboard_profil_list, name="dashboard_profil_list"),
    path("profils/nouveau/", views.dashboard_profil_create, name="dashboard_profil_create"),
    path("profils/<int:pk>/modifier/", views.dashboard_profil_update, name="dashboard_profil_update"),
    path("profils/<int:pk>/supprimer/", views.dashboard_profil_delete, name="dashboard_profil_delete"),

    path("messages/", views.dashboard_message_list, name="dashboard_message_list"),
    path("messages/<int:pk>/", views.dashboard_message_detail, name="dashboard_message_detail"),

    # --- Démarches en ligne (nouveau) ---
    path("demandes/", views.dashboard_demande_list, name="dashboard_demande_list"),
    path("demandes/<int:pk>/", views.dashboard_demande_detail, name="dashboard_demande_detail"),

    # --- Signalements citoyens (réservé à l'administration) ---
    path("signalements/", views.dashboard_signalement_list, name="dashboard_signalement_list"),
    path("signalements/<int:pk>/", views.dashboard_signalement_detail, name="dashboard_signalement_detail"),

    # --- Agents (rôles / permissions, réservé aux superviseurs) ---
    path("agents/", views.dashboard_agent_list, name="dashboard_agent_list"),
    path("mon-profil/", views.dashboard_mon_profil, name="dashboard_mon_profil"),
    path("agents/<int:pk>/modifier/", views.dashboard_agent_update, name="dashboard_agent_update"),

    # --- Journal d'audit (réservé aux superviseurs) ---
    path("journal-audit/", views.dashboard_journal_audit_list, name="dashboard_journal_audit_list"),
]