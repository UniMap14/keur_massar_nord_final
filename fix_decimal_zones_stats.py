# -*- coding: utf-8 -*-
"""
Corrige le TypeError "Object of type Decimal is not JSON serializable"
sur la page d'accueil du dashboard (/gestion/), declenche par le
graphique "recouvrement par zone" maintenant que les zones sont
peuplees. Le calcul du taux restait en Decimal ; on le convertit en
float avant le round().

A executer UNE SEULE FOIS, depuis la racine du projet (a cote de
manage.py) :

    python fix_decimal_zones_stats.py
"""
import io

CHEMIN = "foncier/dashboard_views.py"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

ANCRE = (
    '            zones_stats.append({\n'
    '                "nom": zone.nom,\n'
    '                "taux": round((paye_zone / du_zone) * 100, 1),\n'
    '            })'
)

REMPLACEMENT = (
    '            zones_stats.append({\n'
    '                "nom": zone.nom,\n'
    '                "taux": round((float(paye_zone) / float(du_zone)) * 100, 1),\n'
    '            })'
)

if 'round((float(paye_zone) / float(du_zone)) * 100, 1)' in contenu:
    print("OK : deja applique, rien a faire.")
elif ANCRE not in contenu:
    raise SystemExit(
        "ERREUR : ancre introuvable dans foncier/dashboard_views.py.\n"
        "Le fichier a peut-etre deja ete modifie manuellement -- je n'ai rien touche."
    )
else:
    contenu = contenu.replace(ANCRE, REMPLACEMENT, 1)
    with io.open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : taux de recouvrement par zone converti en float (foncier/dashboard_views.py).")
    print("Redemarrez le serveur Django et rechargez /gestion/.")