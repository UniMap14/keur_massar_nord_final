# -*- coding: utf-8 -*-
"""
python audit_simulateur_4_affichage.py

Affiche la partie HTML/JS restante (affichage du resultat + logique de
bascule des champs selon le type d'impot choisi), pour preparer
l'ajout de nouveaux types de taxe.
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


afficher_extrait("foncier/templates/foncier/fiscalite.html", 700, 800, "fiscalite.html - suite panneau simulateur (result box HTML)")
afficher_extrait("foncier/templates/foncier/fiscalite.html", 1010, 1155, "fiscalite.html - script simulateur (bascule champs + appel AJAX + rendu resultat)")