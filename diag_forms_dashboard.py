# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_forms_dashboard.py', encoding='utf-8').read())"
"""
import inspect
import foncier.dashboard_views as dv

for nom in ["ParcelleForm", "InfrastructureForm"]:
    print("=" * 100)
    print(nom)
    print("=" * 100)
    classe = getattr(dv, nom, None)
    if classe is None:
        print("introuvable")
    else:
        print(inspect.getsource(classe))
    print()