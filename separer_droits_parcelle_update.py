# -*- coding: utf-8 -*-
"""
Priorite 1 (securite) : parcelle_update_fiscal (edition depuis la carte
du geoportail admin) n'avait aucun controle de role, et melangeait
champs cadastraux et fiscaux dans le meme appel. On ajoute un controle
de role selon les champs reellement soumis :
  - champs cadastraux (nicad, adresse, type de document, etc.) -> role 'technique'
  - champs fiscaux (statut fiscal, montant, valeur locative)    -> role 'fiscal'
Un Superviseur (ou un compte historique sans role assigne) passe toujours,
via a_role() qui gere deja cette retrocompatibilite.

Idempotent.
"""
CHEMIN = "foncier/views.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# 1) Import de a_role
ANCIEN_IMPORT = '''from .models import Signalement'''
NOUVEAU_IMPORT = '''from .permissions import a_role
from .models import Signalement'''

if 'from .permissions import a_role' in contenu:
    pass
elif ANCIEN_IMPORT not in contenu:
    erreurs.append("ancre d'import introuvable")
else:
    contenu = contenu.replace(ANCIEN_IMPORT, NOUVEAU_IMPORT, 1)
    remplacements_ok += 1

# 2) Controle de role selon les champs soumis, dans parcelle_update_fiscal
ANCIEN_GARDE = '''    try:
        parcelle = Parcelle.objects.get(pk=parcelle_id)
    except Parcelle.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Parcelle introuvable."}, status=404)

    champs_modifies = []'''

NOUVEAU_GARDE = '''    try:
        parcelle = Parcelle.objects.get(pk=parcelle_id)
    except Parcelle.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Parcelle introuvable."}, status=404)

    # --- Controle de role selon les champs soumis (edition depuis la carte) ---
    # Un Gestionnaire/Chef Cadastre peut modifier les champs cadastraux, mais
    # pas les champs fiscaux, et inversement pour le service Fiscalite. Le
    # Superviseur (et un compte historique sans role assigne) passe toujours
    # via a_role(). Evite qu'un agent d'un service modifie les donnees de
    # l'autre service via ce point d'entree (contrairement au dashboard
    # classique qui etait deja correctement restreint).
    CHAMPS_CADASTRAUX = {
        "nicad", "adresse_parcelle", "type_document", "occupation_sol",
        "reference_arrete", "section_cadastrale", "numero_parcelle",
        "numero_lot", "numero_titre_foncier", "proprietaire_cni",
    }
    CHAMPS_FISCAUX = {"statut_fiscal", "montant_taxe_annuelle", "valeur_locative"}

    champs_soumis = set(request.POST.keys())
    if (champs_soumis & CHAMPS_CADASTRAUX) and not a_role(request.user, 'technique'):
        return JsonResponse({
            "ok": False,
            "error": "Vous n'avez pas les droits pour modifier les informations cadastrales de cette parcelle."
        }, status=403)
    if (champs_soumis & CHAMPS_FISCAUX) and not a_role(request.user, 'fiscal'):
        return JsonResponse({
            "ok": False,
            "error": "Vous n'avez pas les droits pour modifier les informations fiscales de cette parcelle."
        }, status=403)

    champs_modifies = []'''

if 'CHAMPS_CADASTRAUX = {' in contenu:
    pass
elif ANCIEN_GARDE not in contenu:
    erreurs.append("ancre de garde de role introuvable")
else:
    contenu = contenu.replace(ANCIEN_GARDE, NOUVEAU_GARDE, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")