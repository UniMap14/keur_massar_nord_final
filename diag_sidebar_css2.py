# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_sidebar_css2.py', encoding='utf-8').read())"
"""
chemin = "foncier/static/dashboard/css/dashboard.css"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

idx = contenu.find("SIDEBAR")
print(contenu[max(0, idx - 10): idx + 600])