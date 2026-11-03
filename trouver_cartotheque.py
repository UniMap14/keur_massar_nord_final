# -*- coding: utf-8 -*-
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

racine = os.getcwd()

print("=== Fichiers contenant 'cartotheque' (nom ou contenu) ===")
motif = re.compile(r"cartotheque", re.IGNORECASE)
for base, dirs, files in os.walk(racine):
    if 'venv' in base or '.git' in base or 'node_modules' in base or '__pycache__' in base:
        continue
    for f in files:
        if f.endswith((".py", ".html")):
            chemin = os.path.join(base, f)
            trouve_nom = bool(motif.search(f))
            try:
                with io.open(chemin, "r", encoding="utf-8", errors="replace") as fp:
                    contenu = fp.read()
            except Exception:
                continue
            if trouve_nom or motif.search(contenu):
                rel = os.path.relpath(chemin, racine)
                print(rel, "(nom)" if trouve_nom else "")

print()
print("=== Lignes precises dans foncier/urls.py et foncier/views.py ===")
for chemin in ["foncier/urls.py", "foncier/views.py"]:
    with io.open(chemin, "r", encoding="utf-8", errors="replace") as fp:
        lignes = fp.readlines()
    for i, l in enumerate(lignes, 1):
        if motif.search(l):
            print(f"{chemin}:{i}: {l.strip()}")