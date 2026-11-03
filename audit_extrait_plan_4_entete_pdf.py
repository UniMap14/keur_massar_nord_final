# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('audit_extrait_plan_4_entete_pdf.py', encoding='utf-8').read())"

Affiche la source complete de _preparer_pdf_document et _pied_de_page_document
(utilisees par tous les PDF officiels de l'appli, dont l'extrait de plan),
pour savoir exactement ce qu'elles dessinent deja avant de refaire la mise
en page de l'extrait de plan.
"""
import foncier.views as v
import inspect

for nom in ["_preparer_pdf_document", "_pied_de_page_document"]:
    fonction = getattr(v, nom, None)
    print("=" * 100)
    print(nom)
    print("=" * 100)
    if fonction is None:
        print("INTROUVABLE dans foncier.views")
        continue
    try:
        print(inspect.getsource(fonction))
    except Exception as e:
        print("Impossible de recuperer la source :", e)
    print()