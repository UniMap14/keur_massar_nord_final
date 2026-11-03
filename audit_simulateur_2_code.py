# -*- coding: utf-8 -*-
"""
python audit_simulateur_2_code.py

Affiche le code exact actuel du simulateur fiscal (formulaire, vue,
template) pour preparer les ameliorations. Pas besoin de Django.
"""
import io


def afficher_extrait(chemin, debut, fin, titre):
    print("=" * 100)
    print(f"{titre}  ({chemin}, lignes {debut} a {fin})")
    print("=" * 100)
    with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
        lignes = f.readlines()
    debut_idx = max(0, debut - 1)
    fin_idx = min(len(lignes), fin)
    for i in range(debut_idx, fin_idx):
        print(f"{i + 1:5d} | {lignes[i].rstrip()}")
    print()


afficher_extrait("foncier/forms.py", 100, 190, "forms.py - SimulateurFiscalForm")
afficher_extrait("foncier/views.py", 980, 1070, "views.py - vue du simulateur")
afficher_extrait("foncier/templates/foncier/fiscalite.html", 600, 700, "fiscalite.html - panneau simulateur (HTML)")
afficher_extrait("foncier/templates/foncier/fiscalite.html", 950, 1010, "fiscalite.html - script simulateur (JS)")