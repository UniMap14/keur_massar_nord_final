# -*- coding: utf-8 -*-
"""
Ajoute nb_notifications_total au context processor dashboard_counts,
pour alimenter le badge de la cloche de notifications du topbar.
Reutilise peut_technique deja calcule (evite un appel a_role() en double).

Idempotent.
"""
CHEMIN = "foncier/context_processors.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''    return {
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
    }'''

NOUVEAU = '''    peut_technique = a_role(request.user, "technique")

    nb_notifications_total = (
        nb_messages_non_traites
        + nb_demandes_a_traiter
        + nb_inscriptions_en_attente
        + (nb_signalements_en_cours if peut_technique else 0)
    )

    return {
        "nb_messages_non_traites": nb_messages_non_traites,
        "nb_demandes_a_traiter": nb_demandes_a_traiter,
        "nb_inscriptions_en_attente": nb_inscriptions_en_attente,
        "nb_signalements_en_cours": nb_signalements_en_cours,
        "nb_notifications_total": nb_notifications_total,
        "libelle_role_utilisateur": libelle_role(request.user),
        "peut_fiscal": a_role(request.user, "fiscal"),
        "peut_technique": peut_technique,
        "est_superviseur": (
            request.user.is_superuser
            or request.user.groups.filter(name="Superviseur").exists()
        ),
    }'''

if '"nb_notifications_total"' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (return du dict dashboard_counts)")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")