# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def extraire(chemin, lignes_cibles, avant=10, apres=35):
    with io.open(chemin, "r", encoding="utf-8") as f:
        lignes = f.readlines()
    for cible in lignes_cibles:
        debut = max(0, cible - 1 - avant)
        fin = min(len(lignes), cible - 1 + apres)
        print()
        print("=" * 70)
        print(f"{chemin} autour de la ligne {cible}")
        print("=" * 70)
        for i in range(debut, fin):
            print(f"{i+1}: {lignes[i]}", end="")
        print()

extraire("foncier/dashboard_views.py", [479, 658, 688, 713, 761, 901, 1139, 1211, 1297])
extraire("foncier/views.py", [1094, 1342, 1506])