# -*- coding: utf-8 -*-
"""
python audit_simulateur_5_select.py

Dernier morceau manquant avant de patcher le template : le <select> du
type d'impot et les blocs de champs conditionnels (#champ-ca-is,
#champ-situation, #champ-enfants, #champ-secteur) + le bouton Calculer,
pour pouvoir y ajouter proprement les champs CFPB / CEL-VL.
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


afficher_extrait("foncier/templates/foncier/fiscalite.html", 595, 700, "fiscalite.html - select type d'impot + champs conditionnels")