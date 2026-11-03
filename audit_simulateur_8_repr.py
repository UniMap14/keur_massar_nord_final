# -*- coding: utf-8 -*-
"""
python audit_simulateur_8_repr.py

La modification #4 ne correspond toujours pas. On affiche cette fois
les lignes en repr() (affiche les caracteres caches : apostrophes
courbes, espaces, etc.) pour trouver l'ecart exact.
"""
import io

chemin = "foncier/templates/foncier/fiscalite.html"

with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
    lignes = f.readlines()

print(f"Fichier : {chemin} ({len(lignes)} lignes)\n")
for i in range(1130, 1148):
    if i < len(lignes):
        print(f"{i + 1:5d} | {lignes[i].rstrip()!r}")