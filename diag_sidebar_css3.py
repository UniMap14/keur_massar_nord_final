# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_sidebar_css3.py', encoding='utf-8').read())"
"""
chemin = "foncier/static/dashboard/css/dashboard.css"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

for motif in [".sidebar-user .who", ".sidebar-logout"]:
    idx = contenu.find(motif)
    print("=" * 100)
    print(f"'{motif}' -> position {idx}")
    print("=" * 100)
    if idx != -1:
        print(repr(contenu[idx:idx + 400]))
    print()