from django.contrib import admin

from .models import ProjetJeune, MessageProjet, RessourceJeune


class MessageProjetInline(admin.TabularInline):
    model = MessageProjet
    extra = 0
    readonly_fields = ("envoye_par", "date_envoi")


@admin.register(ProjetJeune)
class ProjetJeuneAdmin(admin.ModelAdmin):
    list_display = ("titre_projet", "nom_porteur", "secteur", "statut", "contacte", "date_soumission")
    list_filter = ("statut", "secteur", "besoin_principal", "contacte")
    search_fields = ("titre_projet", "nom_porteur", "telephone", "email")
    inlines = [MessageProjetInline]


@admin.register(RessourceJeune)
class RessourceJeuneAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "ordre")
    list_filter = ("categorie",)
