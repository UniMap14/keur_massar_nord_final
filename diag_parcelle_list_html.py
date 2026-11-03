# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_parcelle_list_html.py', encoding='utf-8').read())"
"""
chemin = "foncier/templates/dashboard/parcelle_list.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    print(f.read())