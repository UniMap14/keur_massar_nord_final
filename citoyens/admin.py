from django.contrib import admin

from .models import Citoyen


@admin.register(Citoyen)
class CitoyenAdmin(admin.ModelAdmin):
    list_display = ("user", "numero_fiscal", "numero_foncier", "statut", "date_inscription")
    list_filter = ("statut",)
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "numero_fiscal", "numero_foncier")
    readonly_fields = ("date_inscription",)
    actions = ["valider_selection", "rejeter_selection"]

    @admin.action(description="Valider les inscriptions sélectionnées")
    def valider_selection(self, request, queryset):
        from django.utils import timezone
        queryset.update(statut=Citoyen.STATUT_VALIDE, date_validation=timezone.now(), valide_par=request.user)

    @admin.action(description="Rejeter les inscriptions sélectionnées")
    def rejeter_selection(self, request, queryset):
        from django.utils import timezone
        queryset.update(statut=Citoyen.STATUT_REJETE, date_validation=timezone.now(), valide_par=request.user)