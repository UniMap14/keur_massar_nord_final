from django.urls import path

from . import views

urlpatterns = [
    path("", views.espace_jeunes_accueil, name="espace_jeunes"),
    path("soumettre/", views.soumettre_projet, name="jeunesse_soumettre"),
    path("merci/", views.merci_projet, name="jeunesse_merci"),
    path("ressources/", views.ressources_jeunes, name="jeunesse_ressources"),

    # Gestion (agents)
    path("gestion/projets-jeunes/", views.gestion_projets_jeunes, name="gestion_projets_jeunes"),
]
