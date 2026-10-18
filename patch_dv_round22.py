# -*- coding: utf-8 -*-
"""
Round 22 (dashboard_views.py) : remplace le contenu du donut
"Repartition par type" -- au lieu de la repartition par type de taxe
(peu parlante avec un seul type de taxe reel), affiche 3 categories
reelles : infrastructures situees dans une parcelle (lien reel
Infrastructure.parcelle), parcelles contribuables (proprietaire ayant
un Contribuable associe), parcelles non contribuables (le reste).

Conserve les noms de variables labels_taxes/valeurs_taxes : le reste
du contexte, le graphique Chart.js et la legende HTML n'ont donc pas
besoin d'etre modifies.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/dashboard_views.py")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE = """    repartition_taxes = (
        Taxation.objects.values("type_taxe__libelle")
        .annotate(total=Sum("montant_du"))
        .order_by("-total")
    )
    labels_taxes = [r["type_taxe__libelle"] for r in repartition_taxes]
    valeurs_taxes = [float(r["total"] or 0) for r in repartition_taxes]"""
AJOUT = """    nb_infra_dans_parcelle = Infrastructure.objects.filter(parcelle__isnull=False).count()

    proprietaires_contribuables_ids = set(
        Contribuable.objects.values_list("proprietaire_id", flat=True)
    )
    nb_parcelles_contribuables = Parcelle.objects.filter(
        proprietaire_id__in=proprietaires_contribuables_ids
    ).count()
    nb_parcelles_non_contribuables = Parcelle.objects.count() - nb_parcelles_contribuables

    labels_taxes = [
        "Infrastructures dans une parcelle",
        "Parcelles contribuables",
        "Parcelles non contribuables",
    ]
    valeurs_taxes = [
        nb_infra_dans_parcelle,
        nb_parcelles_contribuables,
        nb_parcelles_non_contribuables,
    ]"""
if "nb_infra_dans_parcelle = Infrastructure.objects.filter(parcelle__isnull=False).count()" in texte:
    pass
elif ANCRE not in texte:
    erreurs.append("ANCRE introuvable")
else:
    texte = texte.replace(ANCRE, AJOUT, 1)

if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard_views.py -- donut recalcule (infrastructures/parcelles contribuables).")