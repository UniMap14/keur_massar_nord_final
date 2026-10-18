# -*- coding: utf-8 -*-
"""
Round 17 (dashboard_views.py) : retire nb_projets_jeunes (plus utilise
cote template apres le round 17 sur home.html).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE_REQUETE = """    map_nb_parcelles_actives = Parcelle.objects.filter(parcelle_active=True).count()

    from jeunesse.models import ProjetJeune
    nb_projets_jeunes = ProjetJeune.objects.count()"""
AJOUT_REQUETE = """    map_nb_parcelles_actives = Parcelle.objects.filter(parcelle_active=True).count()"""
if ANCRE_REQUETE in texte:
    texte = texte.replace(ANCRE_REQUETE, AJOUT_REQUETE, 1)
elif "nb_projets_jeunes = ProjetJeune.objects.count()" not in texte:
    pass  # deja retire
else:
    erreurs.append("ANCRE_REQUETE introuvable sous la forme exacte attendue")

ANCRE_CONTEXT = """        "map_nb_parcelles_actives": map_nb_parcelles_actives,
        "nb_projets_jeunes": nb_projets_jeunes,"""
AJOUT_CONTEXT = """        "map_nb_parcelles_actives": map_nb_parcelles_actives,"""
if ANCRE_CONTEXT in texte:
    texte = texte.replace(ANCRE_CONTEXT, AJOUT_CONTEXT, 1)
elif '"nb_projets_jeunes": nb_projets_jeunes,' not in texte:
    pass  # deja retire
else:
    erreurs.append("ANCRE_CONTEXT introuvable sous la forme exacte attendue")

if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard_views.py -- round 17 (nb_projets_jeunes retire).")