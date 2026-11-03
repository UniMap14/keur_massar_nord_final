# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_extrait_plan_5_etat_actuel.py', encoding='utf-8').read())"
"""
import inspect
import foncier.views as v

for nom in ["_generer_image_plan_type_officiel", "extrait_cadastral_pdf_view", "_voisines_parcelle"]:
    print("#" * 100)
    print("#", nom)
    print("#" * 100)
    print(inspect.getsource(getattr(v, nom)))
    print()