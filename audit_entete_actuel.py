# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_entete_actuel.py', encoding='utf-8').read())"
"""
import inspect
import foncier.views as v

source = inspect.getsource(v.extrait_cadastral_pdf_view)
idx = source.find("En-tete administratif")
idx2 = source.find("y -= 9 * mm")
print(source[max(0, idx-20):idx2+20])