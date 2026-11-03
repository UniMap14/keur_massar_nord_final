# -*- coding: utf-8 -*-
"""
Corrige le badge "Demarches en ligne" (sidebar + cloche de notifications)
pour qu'il respecte le meme cloisonnement par service que la page
elle-meme : un Chef/Gestionnaire Fiscal ne doit voir dans ce compteur
que les demandes de categorie FISCALITE, un Chef/Gestionnaire Technique
(Cadastre) que les demandes hors FISCALITE, et les autres (superviseur,
superuser, comptes sans role) voient tout -- exactement la meme regle
que _filtrer_demandes_service() deja utilisee par la page
"Demarches en ligne".

A executer UNE SEULE FOIS, depuis la racine du projet (a cote de
manage.py) :

    python fix_badge_demandes_service.py

Le script est idempotent : le relancer apres coup ne fait rien de plus.
"""
import io

CHEMIN = "foncier/context_processors.py"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

ANCRE = (
    "    try:\n"
    "        nb_demandes_a_traiter = DemandeService.objects.filter(\n"
    "            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]\n"
    "        ).count()\n"
    "    except Exception:\n"
    "        nb_demandes_a_traiter = 0"
)

REMPLACEMENT = (
    "    try:\n"
    "        # Cloisonnement par service : un Chef/Gestionnaire Fiscal ne doit\n"
    "        # voir dans ce badge que ses propres demandes (categorie FISCALITE),\n"
    "        # un Chef/Gestionnaire Technique (Cadastre) que les siennes -- meme\n"
    "        # regle que la page \"Demarches en ligne\" elle-meme.\n"
    "        from .dashboard_views import _filtrer_demandes_service\n"
    "        nb_demandes_a_traiter = _filtrer_demandes_service(\n"
    "            request.user, DemandeService.objects.all()\n"
    "        ).filter(\n"
    "            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]\n"
    "        ).count()\n"
    "    except Exception:\n"
    "        nb_demandes_a_traiter = 0"
)

if "_filtrer_demandes_service(\n            request.user, DemandeService.objects.all()\n        ).filter(" in contenu:
    print("OK : deja applique, rien a faire.")
elif ANCRE not in contenu:
    raise SystemExit(
        "ERREUR : ancre introuvable dans foncier/context_processors.py.\n"
        "Le fichier a peut-etre deja ete modifie manuellement -- je n'ai rien touche."
    )
else:
    contenu = contenu.replace(ANCRE, REMPLACEMENT, 1)
    with io.open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : badge 'Demarches en ligne' desormais cloisonne par service (foncier/context_processors.py).")
    print("Pensez a redemarrer le serveur Django (runserver) pour que le changement soit pris en compte.")