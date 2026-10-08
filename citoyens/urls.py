from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Espace public citoyen
    path("inscription/", views.CitoyenRegisterView.as_view(), name="citoyen_register"),
    path("inscription/en-attente/", views.registration_pending_view, name="citoyen_registration_pending"),
    path("connexion/", views.CitoyenLoginView.as_view(), name="citoyen_login"),
    path("connexion/verification/", views.otp_verify_view, name="citoyen_otp_verify"),
    path("connexion/verification/renvoyer/", views.otp_resend_view, name="citoyen_otp_resend"),
    path("espace/", views.espace_personnel_view, name="citoyen_espace"),
    path("espace/parcelles.geojson", views.parcelles_geojson_view, name="parcelles_geojson"),
    path("espace/taxations/<int:pk>/payer/", views.payer_taxation_view, name="citoyen_payer_taxation"),
    path("espace/taxations/paiement/<int:pk>/retour/", views.paiement_retour_view, name="citoyen_paiement_retour"),

    # Profil personnel
    path("espace/profil/", views.modifier_profil_view, name="citoyen_modifier_profil"),
    path(
        "espace/mot-de-passe/",
        auth_views.PasswordChangeView.as_view(
            template_name="citoyens/espace/changer_mot_de_passe.html",
            success_url=reverse_lazy("citoyen_password_change_done"),
        ),
        name="citoyen_password_change",
    ),
    path(
        "espace/mot-de-passe/termine/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="citoyens/espace/changer_mot_de_passe_done.html",
        ),
        name="citoyen_password_change_done",
    ),

    # Démarches en ligne
    path("espace/declarations/", views.declarations_liste_view, name="citoyen_declarations"),
        # Recours et redressements fiscaux
    path("espace/recours/", views.recours_liste_view, name="citoyen_recours_liste"),
        # Exonérations fiscales
    path("espace/exonerations/", views.exoneration_liste_view, name="citoyen_exoneration_liste"),
        # Plans de paiement
    path("espace/plans-paiement/", views.plan_paiement_liste_view, name="citoyen_plan_paiement_liste"),
        # Morcellement / fusion de parcelles
    path("espace/morcellement-fusion/", views.morcellement_fusion_liste_view, name="citoyen_morcellement_fusion_liste"),
    path("espace/morcellement-fusion/nouvelle/", views.morcellement_fusion_creer_view, name="citoyen_morcellement_fusion_creer"),
    path("espace/parcelles/<int:pk>/historique/", views.historique_parcelle_view, name="citoyen_historique_parcelle"),
    path("espace/plans-paiement/taxation/<int:taxation_pk>/nouveau/", views.plan_paiement_creer_view, name="citoyen_plan_paiement_creer"),
    path("espace/echeances/<int:echeance_pk>/payer/", views.echeance_payer_view, name="citoyen_echeance_payer"),
    path("espace/exonerations/parcelle/<int:parcelle_pk>/nouvelle/", views.exoneration_creer_view, name="citoyen_exoneration_creer"),
    path("espace/recours/taxation/<int:taxation_pk>/nouveau/", views.recours_creer_view, name="citoyen_recours_creer"),
    path("espace/recours/<int:recours_pk>/redressement/", views.recours_redressement_creer_view, name="citoyen_recours_redressement"),
        # Calendrier fiscal
    path("espace/calendrier/", views.calendrier_fiscal_view, name="citoyen_calendrier_fiscal"),
    path("espace/declarations/nouvelle/", views.declaration_creer_view, name="citoyen_declaration_creer"),
    path("espace/demarches/", views.demandes_liste_view, name="citoyen_demandes"),
    path("espace/demarches/nouvelle/", views.demande_creer_view, name="citoyen_demande_creer"),
    path("espace/demarches/<int:pk>/", views.demande_detail_view, name="citoyen_demande_detail"),
    path("espace/demarches/<int:pk>/piece-jointe/", views.demande_piece_jointe_view, name="demande_piece_jointe"),
    path("espace/demarches/<int:pk>/payer/", views.demande_payer_view, name="citoyen_demande_payer"),
    # Espace gestion (agents / administration)
    path("gestion/inscriptions/", views.gestion_inscriptions_view, name="gestion_inscriptions"),
]