# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_creation_geom.py', encoding='utf-8').read())"

Etat des lieux de la creation de Parcelle et d'Infrastructure :
- comment la geometrie est saisie aujourd'hui (champ texte brut ? carte ? rien ?)
- quels formulaires/templates sont utilises
"""
import inspect
import foncier.dashboard_views as dv

for nom in ["dashboard_parcelle_create", "dashboard_infrastructure_create"]:
    print("=" * 100)
    print(nom)
    print("=" * 100)
    try:
        print(inspect.getsource(getattr(dv, nom)))
    except Exception as e:
        print("Erreur :", e)
    print()

print("=" * 100)
print("Formulaires ParcelleForm / InfrastructureForm (si trouvables)")
print("=" * 100)
import foncier.forms as forms_module
for nom in dir(forms_module):
    if "Parcelle" in nom or "Infrastructure" in nom:
        classe = getattr(forms_module, nom)
        if hasattr(classe, "Meta"):
            print(f"--- {nom} ---")
            try:
                print(inspect.getsource(classe))
            except Exception as e:
                print("Erreur :", e)
            print()