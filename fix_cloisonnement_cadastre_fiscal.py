# -*- coding: utf-8 -*-
"""
Cloisonne la liste et le traitement des "Demandes de service"
(demarches en ligne, dont l'extrait cadastral) par service :

  - Un agent/chef FISCAL ne voit et ne peut traiter que les demandes
    de categorie 'FISCALITE'.
  - Un agent/chef CADASTRE (technique) voit et traite tout le reste
    (CADASTRE, ETAT_CIVIL, URBANISME, AUTRE) — c'est le "guichet"
    generaliste pour les demarches non fiscales.
  - Superviseur et comptes sans role assigne (retrocompatibilite) :
    acces complet, inchange.

Idempotent : si deja applique, ne touche a rien.
"""
import io

CHEMIN = r"foncier\dashboard_views.py"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

modifie = False

# --- 1. Inserer les fonctions utilitaires de cloisonnement ---
ANCRE_HELPERS = (
    "@staff_member_required(login_url='dashboard_login')\n"
    "def dashboard_demande_list(request):"
)
BLOC_HELPERS = '''def _filtrer_demandes_service(user, queryset):
    """Restreint un queryset de DemandeService au service (cadastre ou
    fiscal) de l'utilisateur. Superviseur, superuser et comptes sans
    role assigne (retrocompatibilite) voient tout."""
    from .permissions import (
        GROUPE_SUPERVISEUR, GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE,
        GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL, GROUPES_ROLES,
    )
    if user.is_superuser:
        return queryset
    noms = set(user.groups.values_list("name", flat=True))
    if GROUPE_SUPERVISEUR in noms:
        return queryset
    if not (noms & set(GROUPES_ROLES)):
        return queryset
    if noms & {GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL}:
        return queryset.filter(type_demande__categorie="FISCALITE")
    if noms & {GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE}:
        return queryset.exclude(type_demande__categorie="FISCALITE")
    return queryset


def _verifier_acces_demande(user, demande):
    """Leve PermissionDenied si l'utilisateur n'a pas le droit de voir/
    traiter cette demande au vu de son service (cadastre ou fiscal)."""
    from .permissions import (
        GROUPE_SUPERVISEUR, GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE,
        GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL, GROUPES_ROLES,
    )
    if user.is_superuser:
        return
    noms = set(user.groups.values_list("name", flat=True))
    if GROUPE_SUPERVISEUR in noms:
        return
    if not (noms & set(GROUPES_ROLES)):
        return
    categorie = demande.type_demande.categorie
    if (noms & {GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL}) and categorie != "FISCALITE":
        raise PermissionDenied(
            "Cette demande relève du service Cadastre, pas du service Fiscalité."
        )
    if (noms & {GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE}) and categorie == "FISCALITE":
        raise PermissionDenied(
            "Cette demande relève du service Fiscalité, pas du service Cadastre."
        )


@staff_member_required(login_url='dashboard_login')
def dashboard_demande_list(request):'''

if "_filtrer_demandes_service" not in contenu:
    if ANCRE_HELPERS not in contenu:
        raise SystemExit("ERREUR : ancre A introuvable (dashboard_demande_list). Fichier modifie ?")
    contenu = contenu.replace(ANCRE_HELPERS, BLOC_HELPERS, 1)
    modifie = True

# --- 2. Appliquer le filtre dans dashboard_demande_list ---
ANCRE_QS = (
    "    demandes = DemandeService.objects.select_related(\n"
    "        \"type_demande\", \"demandeur\", \"parcelle\", \"agent_traitant\"\n"
    "    ).order_by(\"-date_demande\")\n"
    "\n"
    "    if filtre:"
)
REMPLACEMENT_QS = (
    "    demandes = DemandeService.objects.select_related(\n"
    "        \"type_demande\", \"demandeur\", \"parcelle\", \"agent_traitant\"\n"
    "    ).order_by(\"-date_demande\")\n"
    "    demandes = _filtrer_demandes_service(request.user, demandes)\n"
    "\n"
    "    if filtre:"
)
if "demandes = _filtrer_demandes_service(request.user, demandes)" not in contenu:
    if ANCRE_QS not in contenu:
        raise SystemExit("ERREUR : ancre B introuvable (queryset demandes). Fichier modifie ?")
    contenu = contenu.replace(ANCRE_QS, REMPLACEMENT_QS, 1)
    modifie = True

# --- 3. Restreindre les compteurs nb_a_traiter / nb_mes_dossiers au meme service ---
ANCRE_COMPTEURS = (
    '        "nb_a_traiter": DemandeService.objects.filter(\n'
    "            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]\n"
    "        ).count(),\n"
    '        "nb_mes_dossiers": DemandeService.objects.filter(\n'
    "            agent_traitant=request.user,\n"
    "            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS],\n"
    "        ).count(),"
)
REMPLACEMENT_COMPTEURS = (
    '        "nb_a_traiter": _filtrer_demandes_service(\n'
    "            request.user, DemandeService.objects.all()\n"
    "        ).filter(\n"
    "            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]\n"
    "        ).count(),\n"
    '        "nb_mes_dossiers": _filtrer_demandes_service(\n'
    "            request.user, DemandeService.objects.all()\n"
    "        ).filter(\n"
    "            agent_traitant=request.user,\n"
    "            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS],\n"
    "        ).count(),"
)
if "_filtrer_demandes_service(\n            request.user, DemandeService.objects.all()" not in contenu:
    if ANCRE_COMPTEURS not in contenu:
        raise SystemExit("ERREUR : ancre C introuvable (compteurs). Fichier modifie ?")
    contenu = contenu.replace(ANCRE_COMPTEURS, REMPLACEMENT_COMPTEURS, 1)
    modifie = True

# --- 4. Garde d'acces dans dashboard_demande_detail ---
ANCRE_DETAIL = (
    "def dashboard_demande_detail(request, pk):\n"
    "    demande = get_object_or_404(\n"
    '        DemandeService.objects.select_related("type_demande", "demandeur", "parcelle", "agent_traitant"),\n'
    "        pk=pk,\n"
    "    )\n"
    "\n"
    "    if request.method == \"POST\":"
)
REMPLACEMENT_DETAIL = (
    "def dashboard_demande_detail(request, pk):\n"
    "    demande = get_object_or_404(\n"
    '        DemandeService.objects.select_related("type_demande", "demandeur", "parcelle", "agent_traitant"),\n'
    "        pk=pk,\n"
    "    )\n"
    "    _verifier_acces_demande(request.user, demande)\n"
    "\n"
    "    if request.method == \"POST\":"
)
if "_verifier_acces_demande(request.user, demande)" not in contenu:
    if ANCRE_DETAIL not in contenu:
        raise SystemExit("ERREUR : ancre D introuvable (dashboard_demande_detail). Fichier modifie ?")
    contenu = contenu.replace(ANCRE_DETAIL, REMPLACEMENT_DETAIL, 1)
    modifie = True

if modifie:
    with io.open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : cloisonnement cadastre/fiscal applique sur les demandes de service.")
else:
    print("OK : deja a jour, rien a faire.")