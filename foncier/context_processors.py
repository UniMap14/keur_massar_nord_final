# ============================================================
# foncier/context_processors.py
#
# Context processor injectant des compteurs globaux (badges de
# notification) disponibles dans TOUS les templates, sans que
# chaque vue ait à les recalculer manuellement.
#
# Pour l'activer, ajouter le chemin ci-dessous dans
# TEMPLATES[0]["OPTIONS"]["context_processors"] de settings.py :
#
#   "foncier.context_processors.dashboard_counts",
# ============================================================

from .models import MessageContact, DemandeService, Signalement
from .permissions import a_role, libelle_role


def dashboard_counts(request):
    """
    Ajoute nb_messages_non_traites, nb_demandes_a_traiter et
    nb_inscriptions_en_attente au contexte de chaque template, uniquement
    pour les utilisateurs staff connectés (pour éviter une requête DB
    inutile sur les pages du site public).
    """
    if not (hasattr(request, "user") and request.user.is_authenticated and request.user.is_staff):
        return {}

    try:
        nb_messages_non_traites = MessageContact.objects.filter(traite=False).count()
    except Exception:
        # Sécurité : si la table n'existe pas encore (migrations non appliquées),
        # on n'empêche pas le reste du site de fonctionner.
        nb_messages_non_traites = 0

    try:
        nb_demandes_a_traiter = DemandeService.objects.filter(
            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]
        ).count()
    except Exception:
        nb_demandes_a_traiter = 0

    try:
        from citoyens.models import Citoyen
        nb_inscriptions_en_attente = Citoyen.objects.filter(statut=Citoyen.STATUT_EN_ATTENTE).count()
    except Exception:
        nb_inscriptions_en_attente = 0

    try:
        nb_signalements_en_cours = Signalement.objects.filter(statut="EN_COURS").count()
    except Exception:
        nb_signalements_en_cours = 0

    return {
        "nb_messages_non_traites": nb_messages_non_traites,
        "nb_demandes_a_traiter": nb_demandes_a_traiter,
        "nb_inscriptions_en_attente": nb_inscriptions_en_attente,
        "nb_signalements_en_cours": nb_signalements_en_cours,
        "libelle_role_utilisateur": libelle_role(request.user),
        "peut_fiscal": a_role(request.user, "fiscal"),
        "peut_technique": a_role(request.user, "technique"),
        "est_superviseur": (
            request.user.is_superuser
            or request.user.groups.filter(name="Superviseur").exists()
        ),
    }