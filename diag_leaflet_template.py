# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_leaflet_template.py', encoding='utf-8').read())"
"""
import os

for chemin in [
    "foncier/templates/dashboard/widgets/leaflet_polygon.html",
]:
    print("=" * 100)
    print(chemin, "-> existe :", os.path.exists(chemin))
    print("=" * 100)
    if os.path.exists(chemin):
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            print(f.read())
    print()