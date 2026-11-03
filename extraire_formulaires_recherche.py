# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

fichiers = [
    "foncier/templates/dashboard/actualite_list.html",
    "foncier/templates/dashboard/base.html",
    "foncier/templates/dashboard/categorie_list.html",
    "foncier/templates/dashboard/generic_list_stub.html",
    "foncier/templates/dashboard/infrastructure_list.html",
    "foncier/templates/dashboard/parcelle_list.html",
    "foncier/templates/dashboard/recherche_cadastrale.html",
    "foncier/templates/foncier/actualites_liste.html",
    "foncier/templates/foncier/recherche_cadastrale.html",
    "foncier/templates/foncier/recherche_globale.html",
]

for chemin in fichiers:
    try:
        with io.open(chemin, "r", encoding="utf-8", errors="replace") as f:
            lignes = f.readlines()
    except FileNotFoundError:
        print()
        print("=" * 70)
        print(chemin, "- FICHIER INTROUVABLE")
        continue

    indices = [i for i, l in enumerate(lignes) if re.search(r"<form|type=[\"']search[\"']|name=[\"'](q|recherche|search)[\"']", l, re.IGNORECASE)]
    if not indices:
        print()
        print("=" * 70)
        print(chemin, "- aucun <form>/input de recherche trouve (recherche peut-etre en JS pur)")
        continue

    print()
    print("=" * 70)
    print(chemin)
    print("=" * 70)
    deja_imprime = set()
    for idx in indices:
        debut = max(0, idx - 3)
        fin = min(len(lignes), idx + 12)
        for i in range(debut, fin):
            if i not in deja_imprime:
                print(f"{i+1}: {lignes[i]}", end="")
                deja_imprime.add(i)
        print("...")