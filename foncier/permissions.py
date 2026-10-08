# ============================================================
# foncier/permissions.py
#
# Permissions par service (rôle) pour l'espace de gestion, basées sur
# les groupes Django standards (gérables depuis /admin/auth/group/ ou
# depuis la page "Agents" du dashboard — voir dashboard_agent_list).
#
# Cinq groupes, organisés en deux services + le sommet hiérarchique :
#   - Superviseur         : accès à tout, aucune restriction (Maire).
#   - Chef Cadastre        : tout ce que fait un Gestionnaire Cadastre,
#                            PLUS la suppression, les validations et
#                            les traitements réservés (signature).
#   - Gestionnaire Cadastre: opérations courantes sur les parcelles,
#                            propriétaires, zones, infrastructures,
#                            catégories d'infra., actualités.
#   - Chef Fiscalité        : tout ce que fait un Gestionnaire Fiscalité,
#                            PLUS la suppression, les validations et
#                            les traitements réservés (signature).
#   - Gestionnaire Fiscalité: opérations courantes sur les contribuables,
#                            taxations, paiements, types de taxe,
#                            profils citoyens.
#
# Deux niveaux de vérification par service :
#   - role_requis('technique') / role_requis('fiscal')
#       -> accessible aux GESTIONNAIRES et aux CHEFS du service (le
#          chef peut toujours faire ce que fait un gestionnaire).
#   - role_requis('chef_technique') / role_requis('chef_fiscal')
#       -> réservé aux CHEFS uniquement (suppression, validation,
#          signature, traitement des demandes).
#
# Sections communes à tous les agents (aucune restriction de rôle) :
# tableau de bord, messages de contact, démarches en ligne, inscriptions
# citoyens — ce sont des tâches d'accueil général, pas propres à un
# service.
#
# RÉTROCOMPATIBILITÉ : un compte staff qui n'a encore été assigné à
# AUCUN des 5 groupes ci-dessous garde un accès complet (comme avant
# la mise en place des rôles), pour ne bloquer aucun compte existant
# tant que l'administration n'a pas explicitement choisi un rôle pour
# lui depuis la page "Agents".
# ============================================================

from functools import wraps
from django.core.exceptions import PermissionDenied

GROUPE_SUPERVISEUR = "Superviseur"
GROUPE_CHEF_TECHNIQUE = "Chef Cadastre"
GROUPE_GESTIONNAIRE_TECHNIQUE = "Gestionnaire Cadastre"
GROUPE_CHEF_FISCAL = "Chef Fiscalité"
GROUPE_GESTIONNAIRE_FISCAL = "Gestionnaire Fiscalité"

GROUPES_ROLES = [
    GROUPE_SUPERVISEUR,
    GROUPE_CHEF_TECHNIQUE,
    GROUPE_GESTIONNAIRE_TECHNIQUE,
    GROUPE_CHEF_FISCAL,
    GROUPE_GESTIONNAIRE_FISCAL,
]

# Groupes qui donnent accès à role_requis('technique') / role_requis('fiscal')
# (le service au sens large : chef + gestionnaire).
GROUPES_SERVICE_TECHNIQUE = {GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE}
GROUPES_SERVICE_FISCAL = {GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL}

# Groupes qui donnent accès à role_requis('chef_technique') / role_requis('chef_fiscal')
# (réservé au chef de service : suppression, validation, signature).
GROUPES_CHEF_TECHNIQUE = {GROUPE_CHEF_TECHNIQUE}
GROUPES_CHEF_FISCAL = {GROUPE_CHEF_FISCAL}

# Correspondance rôle (utilisé dans role_requis(...)) -> ensemble de
# groupes qui satisfont ce rôle.
ROLE_VERS_GROUPES = {
    "superviseur": {GROUPE_SUPERVISEUR},
    "technique": GROUPES_SERVICE_TECHNIQUE,
    "fiscal": GROUPES_SERVICE_FISCAL,
    "chef_technique": GROUPES_CHEF_TECHNIQUE,
    "chef_fiscal": GROUPES_CHEF_FISCAL,
    # Reserve au Gestionnaire SEUL (le Chef ne cree pas de nouvelles entrees,
    # il valide/modifie/supprime ce que le Gestionnaire a saisi).
    "gestionnaire_technique": {GROUPE_GESTIONNAIRE_TECHNIQUE},
    "gestionnaire_fiscal": {GROUPE_GESTIONNAIRE_FISCAL},
}

# Conservé pour compatibilité avec le code existant qui importe
# ROLE_VERS_GROUPE (singulier, un seul groupe par rôle) — utilisé
# uniquement par l'attribution de rôle depuis la page Agents.
ROLE_VERS_GROUPE = {
    "superviseur": GROUPE_SUPERVISEUR,
    "chef_technique": GROUPE_CHEF_TECHNIQUE,
    "technique": GROUPE_GESTIONNAIRE_TECHNIQUE,
    "chef_fiscal": GROUPE_CHEF_FISCAL,
    "fiscal": GROUPE_GESTIONNAIRE_FISCAL,
}


def _noms_groupes(user):
    if not user.is_authenticated:
        return set()
    return set(user.groups.values_list("name", flat=True))


def a_role(user, *roles):
    """True si l'utilisateur a accès à une section nécessitant l'un des
    rôles donnés (ex: a_role(user, 'fiscal'), a_role(user, 'chef_technique'))."""
    if user.is_superuser:
        return True
    noms = _noms_groupes(user)
    if GROUPE_SUPERVISEUR in noms:
        return True
    if not (noms & set(GROUPES_ROLES)):
        # Compte historique sans rôle assigné : accès complet, rétrocompatible.
        return True
    for role in roles:
        if noms & ROLE_VERS_GROUPES.get(role, set()):
            return True
    return False


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
    if GROUPE_CHEF_TECHNIQUE in noms:
        return "Chef du Service Cadastre"
    if GROUPE_GESTIONNAIRE_TECHNIQUE in noms:
        return "Gestionnaire Cadastre"
    if GROUPE_CHEF_FISCAL in noms:
        return "Chef du Service Fiscalité"
    if GROUPE_GESTIONNAIRE_FISCAL in noms:
        return "Gestionnaire Fiscalité"
    return "Agent (tous accès)"