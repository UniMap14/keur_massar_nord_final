# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_creation_geom2.py', encoding='utf-8').read())"
"""
import inspect
import foncier.forms as forms_module

print("Classes dans foncier.forms :", [n for n in dir(forms_module) if n[0].isupper()])
print()

for nom in ["ParcelleForm", "InfrastructureForm"]:
    print("=" * 100)
    print(nom)
    print("=" * 100)
    classe = getattr(forms_module, nom, None)
    if classe is None:
        print("INTROUVABLE dans foncier.forms")
    else:
        try:
            print(inspect.getsource(classe))
        except Exception as e:
            print("Erreur getsource :", e)
    print()

print("=" * 100)
print("Contenu brut de dashboard/parcelle_form.html")
print("=" * 100)
import os
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles")]
    for f in filenames:
        if f in ("parcelle_form.html", "infrastructure_form.html"):
            chemin = os.path.join(dirpath, f)
            print(f"--- {chemin} ---")
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                    print(fh.read())
            except Exception as e:
                print("Erreur :", e)
            print()