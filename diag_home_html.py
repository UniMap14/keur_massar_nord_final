# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_home_html.py', encoding='utf-8').read())"
"""
import os

chemin = "foncier/templates/dashboard/home.html"
print(chemin, "-> existe :", os.path.exists(chemin))
if os.path.exists(chemin):
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        lignes = f.readlines()
    print("LONGUEUR TOTALE (lignes) :", len(lignes))
    print()
    for i, ligne in enumerate(lignes, start=1):
        if "total_recouvre_fmt" in ligne or "peut_fiscal" in ligne or "peut_technique" in ligne \
           or "taux_recouvrement" in ligne or "reste_a_recouvrer_fmt" in ligne:
            debut = max(0, i - 6)
            fin = min(len(lignes), i + 4)
            print(f"--- autour de la ligne {i} ---")
            print("".join(lignes[debut:fin]))
            print()