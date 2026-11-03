# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_settings_cache.py', encoding='utf-8').read())"
"""
import os
import re

# Trouver settings.py
chemin_trouve = None
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (
        ".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles"
    )]
    for f in filenames:
        if f == "settings.py":
            chemin = os.path.join(dirpath, f)
            with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                contenu = fh.read()
            if "CACHES" in contenu:
                chemin_trouve = chemin
                print("Fichier :", chemin)
                m = re.search(r"CACHES\s*=\s*\{.*?\n\}", contenu, re.DOTALL)
                print(m.group(0) if m else "bloc CACHES non trouve par le motif simple")
                print()

if not chemin_trouve:
    print("Aucun settings.py avec CACHES trouve.")