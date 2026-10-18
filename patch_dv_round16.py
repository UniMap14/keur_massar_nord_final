# -*- coding: utf-8 -*-
"""
Round 16 (dashboard_views.py) : ajoute nb_projets_jeunes (compte reel
des ProjetJeune) au contexte du tableau de bord, pour la nouvelle
carte KPI "Projets jeunes".

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE_REQUETE = """    map_nb_parcelles_actives = Parcelle.objects.filter(parcelle_active=True).count()"""
AJOUT_REQUETE = """    map_nb_parcelles_actives = Parcelle.objects.filter(parcelle_active=True).count()

    from jeunesse.models import ProjetJeune
    nb_projets_jeunes = ProjetJeune.objects.count()"""
if "nb_projets_jeunes = ProjetJeune.objects.count()" in texte:
    pass
elif ANCRE_REQUETE not in texte:
    erreurs.append("ANCRE_REQUETE introuvable")
else:
    texte = texte.replace(ANCRE_REQUETE, AJOUT_REQUETE, 1)

ANCRE_CONTEXT = """        "map_nb_parcelles_actives": map_nb_parcelles_actives,"""
AJOUT_CONTEXT = """        "map_nb_parcelles_actives": map_nb_parcelles_actives,
        "nb_projets_jeunes": nb_projets_jeunes,"""
if '"nb_projets_jeunes": nb_projets_jeunes,' in texte:
    pass
elif ANCRE_CONTEXT not in texte:
    erreurs.append("ANCRE_CONTEXT introuvable")
else:
    texte = texte.replace(ANCRE_CONTEXT, AJOUT_CONTEXT, 1)

if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard_views.py -- nb_projets_jeunes ajoute au contexte.")