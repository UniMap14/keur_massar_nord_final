# -*- coding: utf-8 -*-
"""
python audit_simulateur_3_suite.py

Complete l'audit precedent : fin du formulaire (forms.py) et fin de la
vue de calcul (views.py), pour voir la partie CGU et verifier si
secteur_activite est bien declare.
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
    print(f"(fichier total : {len(lignes)} lignes)\n")


afficher_extrait("foncier/forms.py", 190, 260, "forms.py - suite de SimulateurFiscalForm")
afficher_extrait("foncier/views.py", 1067, 1140, "views.py - suite (TVA, CGU) de la vue de calcul")
afficher_extrait("foncier/views.py", 1, 60, "views.py - BAREME_IR et constantes (debut du fichier)")