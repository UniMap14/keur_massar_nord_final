# ============================================================
# foncier/permissions.py
#
# Permissions par service (rôle) pour l'espace de gestion, basées sur
# les groupes Django standards (gérables depuis /admin/auth/group/ ou
# depuis la page "Agents" du dashboard — voir dashboard_agent_list).
#
# Trois rôles :
#   - Superviseur   : accès à tout, aucune restriction.
#   - Agent fiscal  : contribuables, taxations, paiements, types de
#                     taxe, profils citoyens.
#   - Agent technique : parcelles, propriétaires, zones, infrastructures,
#                        catégories d'infra., actualités, signalements.
#
# Sections communes à tous les agents (aucune restriction de rôle) :
# tableau de bord, messages de contact, démarches en ligne, inscriptions
# citoyens — ce sont des tâches d'accueil général, pas propres à un
# service.
#
# RÉTROCOMPATIBILITÉ : un compte staff qui n'a encore été assigné à
# AUCUN des 3 groupes ci-dessous garde un accès complet (comme avant
# la mise en place des rôles), pour ne bloquer aucun compte existant
# tant que l'administration n'a pas explicitement choisi un rôle pour
# lui depuis la page "Agents".
# ============================================================

from functools import wraps
from django.core.exceptions import PermissionDenied

GROUPE_SUPERVISEUR = "Superviseur"
GROUPE_FISCAL = "Agent fiscal"
GROUPE_TECHNIQUE = "Agent technique"

GROUPES_ROLES = [GROUPE_SUPERVISEUR, GROUPE_FISCAL, GROUPE_TECHNIQUE]

ROLE_VERS_GROUPE = {
    "superviseur": GROUPE_SUPERVISEUR,
    "fiscal": GROUPE_FISCAL,
    "technique": GROUPE_TECHNIQUE,
}


def _noms_groupes(user):
    if not user.is_authenticated:
        return set()
    return set(user.groups.values_list("name", flat=True))


def a_role(user, *roles):
    """True si l'utilisateur a accès à une section nécessitant l'un des
    rôles donnés (ex: a_role(user, 'fiscal'))."""
    if user.is_superuser:
        return True
    noms = _noms_groupes(user)
    if GROUPE_SUPERVISEUR in noms:
        return True
    if not (noms & set(GROUPES_ROLES)):
        # Compte historique sans rôle assigné : accès complet, rétrocompatible.
        return True
    return any(ROLE_VERS_GROUPE.get(role) in noms for role in roles)


def role_requis(*roles):
    """Décorateur à empiler APRÈS @staff_member_required (qui gère déjà
    authentification/redirection) : ne fait que vérifier le rôle une
    fois qu'on sait que l'utilisateur est bien un membre du staff connecté."""
    def decorateur(vue):
        @wraps(vue)
        def wrapper(request, *args, **kwargs):
            if not a_role(request.user, *roles):
                raise PermissionDenied("Vous n'avez pas accès à cette section.")
            return vue(request, *args, **kwargs)
        return wrapper
    return decorateur


def libelle_role(user):
    """Libellé lisible du rôle principal de l'utilisateur, pour affichage
    (ex: dans le pied de la sidebar du dashboard)."""
    if user.is_superuser:
        return "Administrateur"
    noms = _noms_groupes(user)
    if GROUPE_SUPERVISEUR in noms:
        return "Superviseur"
    if GROUPE_FISCAL in noms:
        return "Agent fiscal"
    if GROUPE_TECHNIQUE in noms:
        return "Agent technique"
    return "Agent (tous accès)"
