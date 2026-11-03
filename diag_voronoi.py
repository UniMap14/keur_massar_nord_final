# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi.py', encoding='utf-8').read())"

Objectif : localiser tout ce qui existe deja autour de "voronoi" /
"desserte" / "sous-desservie" dans le projet (backend ET frontend),
pour comprendre ce qu'il y a deja avant de l'ameliorer.
"""
import os

MOTS = ["voronoi", "desserte", "desservie", "sous_desservie", "sous-desservie"]

print("=" * 100)
print("1) Fichiers .py contenant l'un de ces mots")
print("=" * 100)
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (
        ".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles"
    )]
    for f in filenames:
        if f.endswith(".py"):
            chemin = os.path.join(dirpath, f)
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                    contenu = fh.read()
            except Exception:
                continue
            bas = contenu.lower()
            trouves = [m for m in MOTS if m in bas]
            if trouves:
                print(chemin, "->", trouves)
print()

print("=" * 100)
print("2) Fichiers .html contenant l'un de ces mots")
print("=" * 100)
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (
        ".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles"
    )]
    for f in filenames:
        if f.endswith(".html"):
            chemin = os.path.join(dirpath, f)
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                    contenu = fh.read()
            except Exception:
                continue
            bas = contenu.lower()
            trouves = [m for m in MOTS if m in bas]
            if trouves:
                print(chemin, "->", trouves)
print()

print("=" * 100)
print("3) Fichiers .js contenant l'un de ces mots")
print("=" * 100)
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (
        ".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles"
    )]
    for f in filenames:
        if f.endswith(".js"):
            chemin = os.path.join(dirpath, f)
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                    contenu = fh.read()
            except Exception:
                continue
            bas = contenu.lower()
            trouves = [m for m in MOTS if m in bas]
            if trouves:
                print(chemin, "->", trouves, "- taille:", len(contenu))