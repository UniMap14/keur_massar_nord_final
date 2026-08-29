from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Espace public citoyen
    path("inscription/", views.CitoyenRegisterView.as_view(), name="citoyen_register"),
    path("inscription/en-attente/", views.registration_pending_view, name="citoyen_registration_pending"),
    path("connexion/", views.CitoyenLoginView.as_view(), name="citoyen_login"),
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
    path("espace/demarches/", views.demandes_liste_view, name="citoyen_demandes"),
    path("espace/demarches/nouvelle/", views.demande_creer_view, name="citoyen_demande_creer"),
    path("espace/demarches/<int:pk>/", views.demande_detail_view, name="citoyen_demande_detail"),
    path("espace/demarches/<int:pk>/piece-jointe/", views.demande_piece_jointe_view, name="demande_piece_jointe"),

    # Espace gestion (agents / administration)
    path("gestion/inscriptions/", views.gestion_inscriptions_view, name="gestion_inscriptions"),
]