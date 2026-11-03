# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_zones3.py', encoding='utf-8').read())"
"""
import os

chemins_possibles = [
    "foncier/import_zones.py",
    "foncier/management/commands/import_zones.py",
]
for chemin in chemins_possibles:
    print("=" * 100)
    print(chemin, "-> existe :", os.path.exists(chemin))
    print("=" * 100)
    if os.path.exists(chemin):
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            print(f.read())
    print()

# Recherche large au cas ou le fichier est ailleurs / nomme differemment
print("=" * 100)
print("Recherche large de fichiers 'import_zones*' dans le projet :")
print("=" * 100)
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles")]
    for f in filenames:
        if "import_zone" in f.lower() or "import_quartier" in f.lower():
            print(os.path.join(dirpath, f))