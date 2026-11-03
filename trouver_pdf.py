# -*- coding: utf-8 -*-
import io, sys, os, re

racine = os.getcwd()

print("=== Recherche de fichiers lies au PDF / extrait ===")
motifs = re.compile(r"(pdf|extrait)", re.IGNORECASE)
for base, dirs, files in os.walk(racine):
    if 'venv' in base or '.git' in base or '__pycache__' in base or 'node_modules' in base:
        continue
    for f in files:
        if motifs.search(f) and (f.endswith('.py') or f.endswith('.html')):
            print(os.path.relpath(os.path.join(base, f), racine))

print()
print("=== Recherche du mot 'pdf' dans foncier/views.py, foncier/dashboard_views.py, citoyens/views.py ===")
for chemin in ["foncier/views.py", "foncier/dashboard_views.py", "citoyens/views.py"]:
    if not os.path.exists(chemin):
        continue
    with io.open(chemin, "r", encoding="utf-8") as fp:
        lignes = fp.readlines()
    for i, ligne in enumerate(lignes):
        if re.search(r"pdf", ligne, re.IGNORECASE):
            print(f"{chemin}:{i+1}: {ligne.rstrip()}")