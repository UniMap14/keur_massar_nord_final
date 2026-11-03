# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_footer.py', encoding='utf-8').read())"

Objectif : localiser le footer du site (public, pas le dashboard admin)
et sa feuille de style actuelle (couleurs sombres a changer en dore).
"""
import os

print("=" * 100)
print("1) Fichiers contenant '<footer' (templates HTML)")
print("=" * 100)
resultats = []
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
            if "<footer" in contenu.lower():
                resultats.append(chemin)
                print(chemin)
print()

print("=" * 100)
print("2) Fichiers CSS contenant '.footer' ou 'footer {'")
print("=" * 100)
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (
        ".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles"
    )]
    for f in filenames:
        if f.endswith(".css"):
            chemin = os.path.join(dirpath, f)
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                    contenu = fh.read()
            except Exception:
                continue
            if "footer" in contenu.lower():
                print(chemin)
print()

print("=" * 100)
print("3) Contenu complet des templates trouves a l'etape 1 (zone <footer> + 40 lignes de contexte)")
print("=" * 100)
for chemin in resultats:
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        contenu = f.read()
    idx = contenu.lower().find("<footer")
    print("-" * 100)
    print(chemin)
    print("-" * 100)
    print(contenu[max(0, idx - 100): idx + 1500])
    print()