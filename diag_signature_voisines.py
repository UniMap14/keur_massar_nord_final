# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_signature_voisines.py', encoding='utf-8').read())"
"""
import inspect
import foncier.views as v

print("Signature actuelle de _voisines_parcelle :")
print(inspect.signature(v._voisines_parcelle))
print()
print("Source complete :")
print(inspect.getsource(v._voisines_parcelle))

print("=" * 100)
print("Nombre d'occurrences de 'def _voisines_parcelle' dans le fichier source")
print("=" * 100)
with open("foncier/views.py", "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()
print(contenu.count("def _voisines_parcelle"))