# -*- coding: utf-8 -*-
import sys, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

racine = os.getcwd()
print("=== Fichiers *urls*.py du projet ===")
for base, dirs, files in os.walk(racine):
    if 'venv' in base or '.git' in base or '__pycache__' in base:
        continue
    for f in files:
        if "urls" in f.lower() and f.endswith(".py"):
            print(os.path.relpath(os.path.join(base, f), racine))

print()
print("=== Recherche de 'dashboard_parcelle_list' dans tout le projet (fichiers .py) ===")
motif = re.compile(r"dashboard_parcelle_list|dashboard_contribuable_list")
for base, dirs, files in os.walk(racine):
    if 'venv' in base or '.git' in base or '__pycache__' in base:
        continue
    for f in files:
        if f.endswith(".py") and "urls" in f.lower():
            chemin = os.path.join(base, f)
            with io.open(chemin, "r", encoding="utf-8", errors="replace") as fp:
                lignes = fp.readlines()
            for i, l in enumerate(lignes, 1):
                if motif.search(l):
                    print(f"{os.path.relpath(chemin, racine)}:{i}: {l.strip()}")