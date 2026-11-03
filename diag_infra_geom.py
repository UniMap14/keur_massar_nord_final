# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_infra_geom.py', encoding='utf-8').read())"
"""
import inspect
import foncier.models as m

print("=" * 100)
print("1) Modele Infrastructure (champs)")
print("=" * 100)
print(inspect.getsource(m.Infrastructure))
print()

print("=" * 100)
print("2) Modele Parcelle : juste le champ 'geom'")
print("=" * 100)
champ = m.Parcelle._meta.get_field("geom")
print("type champ geom Parcelle :", type(champ).__name__, "-", champ)
print()

# Trouver ou vivent ParcelleForm / InfrastructureForm
import os
print("=" * 100)
print("3) Fichiers contenant 'class ParcelleForm' ou 'class InfrastructureForm'")
print("=" * 100)
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles")]
    for f in filenames:
        if f.endswith(".py"):
            chemin = os.path.join(dirpath, f)
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                    contenu = fh.read()
            except Exception:
                continue
            if "class ParcelleForm" in contenu or "class InfrastructureForm" in contenu:
                print(chemin)
print()

print("=" * 100)
print("4) Contenu de foncier/widgets.py (widget carte existant pour Parcelle)")
print("=" * 100)
if os.path.exists("foncier/widgets.py"):
    with open("foncier/widgets.py", "r", encoding="utf-8", errors="replace") as f:
        print(f.read())
else:
    print("foncier/widgets.py introuvable a cet emplacement")