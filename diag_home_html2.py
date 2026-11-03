# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_home_html2.py', encoding='utf-8').read())"
"""
chemin = "foncier/templates/dashboard/home.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    lignes = f.readlines()

print("".join(lignes[714:742]))