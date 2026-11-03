# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_footer_css_full.py', encoding='utf-8').read())"
"""
chemin = "foncier/static/foncier/css/style.css"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

print(contenu[17780:19500])