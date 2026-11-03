# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_fiscal_3_appels_crud.py', encoding='utf-8').read())"

Verifie les appels reels a _crud_views(...) pour Contribuable, Taxation,
Paiement (et les autres CRUD generiques) -- notamment si 'roles=' est
bien passe pour imposer le role fiscal sur creer/modifier/supprimer.
"""
import re

chemin = "foncier/dashboard_views.py"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

for m in re.finditer(r"= _crud_views\(\s*([^\n]*(?:\n[^\n]*)*?)\)\n", contenu):
    bloc = m.group(0)
    if "Contribuable" in bloc or "Taxation" in bloc or "Paiement" in bloc or "Propriétaire" in bloc or "Proprietaire" in bloc or "Infrastructure" in bloc or "Zone" in bloc:
        print("-" * 100)
        print(bloc.strip())
        print()