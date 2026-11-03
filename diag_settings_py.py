# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_settings_py.py', encoding='utf-8').read())"
"""
import os

for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (
        ".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles"
    )]
    for f in filenames:
        if f == "settings.py":
            chemin = os.path.join(dirpath, f)
            print("=" * 100)
            print(chemin)
            print("=" * 100)
            with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                contenu = fh.read()
            # On affiche la fin du fichier (souvent la ou vivent les reglages additionnels)
            print(contenu[-1500:])
            print()
            print("BASE_DIR present :", "BASE_DIR" in contenu)