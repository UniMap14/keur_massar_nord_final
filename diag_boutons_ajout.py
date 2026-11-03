# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_boutons_ajout.py', encoding='utf-8').read())"

Objectif : trouver l'URL exacte des pages de creation Parcelle/Infrastructure,
et verifier si un bouton "+ Nouvelle" existe deja sur les pages de liste.
"""
import os
from django.urls import reverse

print("=" * 100)
print("1) URLs de creation")
print("=" * 100)
for nom in ["dashboard_parcelle_create", "dashboard_infrastructure_create",
            "dashboard_parcelle_list", "dashboard_infrastructure_list"]:
    try:
        print(f"{nom:35s} -> {reverse(nom)}")
    except Exception as e:
        print(f"{nom:35s} -> ERREUR : {e}")
print()

print("=" * 100)
print("2) Les templates de liste contiennent-ils deja un lien vers la creation ?")
print("=" * 100)
for chemin in [
    "foncier/templates/dashboard/parcelle_list.html",
    "foncier/templates/dashboard/infrastructure_list.html",
]:
    print("-" * 100)
    print(chemin, "-> existe :", os.path.exists(chemin))
    if os.path.exists(chemin):
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            contenu = f.read()
        for mot in ["_create", "Nouvelle", "Nouveau", "fa-plus"]:
            idx = contenu.find(mot)
            if idx != -1:
                debut = max(0, idx - 80)
                fin = min(len(contenu), idx + 80)
                print(f"  trouve '{mot}' -> ...{contenu[debut:fin]}...")
    print()