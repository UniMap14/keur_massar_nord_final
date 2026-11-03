# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_footer_vars.py', encoding='utf-8').read())"
"""
import re

chemin = "foncier/static/foncier/css/style.css"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

m = re.search(r":root\s*\{[^}]*\}", contenu, re.DOTALL)
if m:
    print(m.group(0))
else:
    print("Bloc :root introuvable")