# -*- coding: utf-8 -*-
"""
Ajoute l'URL /gestion/recherche/ -> dashboard_recherche_globale dans
foncier/dashboard_urls.py.

Idempotent.
"""
import io

chemin = "foncier/dashboard_urls.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

if "dashboard_recherche_globale" in contenu:
    print("Deja applique, rien a faire.")
else:
    ancre = 'path("", views.dashboard_home, name="dashboard_home"),'
    if ancre not in contenu:
        raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")

    nouvelle_ligne = ancre + '\n    path("recherche/", views.dashboard_recherche_globale, name="dashboard_recherche_globale"),'
    contenu = contenu.replace(ancre, nouvelle_ligne)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")