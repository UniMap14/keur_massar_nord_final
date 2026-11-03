# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== Contenu complet de foncier/permissions.py ===")
with io.open("foncier/permissions.py", "r", encoding="utf-8") as f:
    print(f.read())

print()
print("=== Recherche de 'peut_technique' / 'peut_fiscal' dans le projet (context processors, views) ===")
import os
racine = os.getcwd()
motif = re.compile(r"peut_technique|peut_fiscal|context_processor")
for base, dirs, files in os.walk(racine):
    if 'venv' in base or '.git' in base or 'node_modules' in base or '__pycache__' in base:
        continue
    for f in files:
        if f.endswith(".py"):
            chemin = os.path.join(base, f)
            try:
                with io.open(chemin, "r", encoding="utf-8", errors="replace") as fp:
                    lignes = fp.readlines()
            except Exception:
                continue
            for i, ligne in enumerate(lignes, 1):
                if motif.search(ligne):
                    rel = os.path.relpath(chemin, racine)
                    print(f"{rel}:{i}: {ligne.strip()}")