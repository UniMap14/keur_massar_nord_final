# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_montant_cadastre2.py', encoding='utf-8').read())"
"""
import inspect
import foncier.dashboard_views as dv
import foncier.permissions as perm
import os

print("=" * 100)
print("1) Fin de dashboard_home (contexte renvoye + template utilise)")
print("=" * 100)
source = inspect.getsource(dv.dashboard_home)
lignes_src = source.splitlines()
print("\n".join(lignes_src[120:]))
print()

print("=" * 100)
print("2) foncier/permissions.py (en entier)")
print("=" * 100)
try:
    print(inspect.getsource(perm))
except Exception as e:
    print("Erreur :", e)
print()

print("=" * 100)
print("3) dashboard/dashboard_home.html : recherche de 'total_recouvre' / 'taux_recouvrement' / KPI carte")
print("=" * 100)
chemin = "foncier/templates/dashboard/dashboard_home.html"
print(chemin, "-> existe :", os.path.exists(chemin))
if os.path.exists(chemin):
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        lignes = f.readlines()
    for i, ligne in enumerate(lignes, start=1):
        if "total_recouvre" in ligne or "taux_recouvrement" in ligne or "nb_demandes_en_cours" in ligne:
            debut = max(0, i - 5)
            fin = min(len(lignes), i + 3)
            print(f"--- autour de la ligne {i} ---")
            print("".join(lignes[debut:fin]))
            print()

print("=" * 100)
print("4) context_processors.py : chef_service_flags (en entier)")
print("=" * 100)
import foncier.context_processors as cp
try:
    print(inspect.getsource(cp.chef_service_flags))
except Exception as e:
    print("Erreur :", e)