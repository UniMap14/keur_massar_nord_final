# -*- coding: utf-8 -*-
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

racine = os.getcwd()

print("=== Templates contenant un champ de recherche (input search/recherche/q) ===")
motif_template = re.compile(r"type=[\"']search[\"']|name=[\"'](q|recherche|search|query)[\"']", re.IGNORECASE)
for base, dirs, files in os.walk(racine):
    if 'venv' in base or '.git' in base or 'node_modules' in base or '__pycache__' in base:
        continue
    for f in files:
        if f.endswith(".html"):
            chemin = os.path.join(base, f)
            try:
                with io.open(chemin, "r", encoding="utf-8", errors="replace") as fp:
                    contenu = fp.read()
            except Exception:
                continue
            if motif_template.search(contenu):
                rel = os.path.relpath(chemin, racine)
                print(rel)

print()
print("=== Vues utilisant request.GET.get('q'/'recherche'/'search'/'query') ===")
motif_vue = re.compile(r"request\.GET\.get\(['\"](q|recherche|search|query)['\"]", re.IGNORECASE)
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
                if motif_vue.search(ligne):
                    rel = os.path.relpath(chemin, racine)
                    print(f"{rel}:{i}: {ligne.strip()}")