# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_dashboard_home.py', encoding='utf-8').read())"
"""
import inspect
import foncier.dashboard_views as dv

print(inspect.getsource(dv.dashboard_home))