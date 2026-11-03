# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi2.py', encoding='utf-8').read())"

Objectif : voir la structure (tailles, fonctions JS, commentaires) de la
partie "analyse desserte / voronoi / sous-desservie" dans le geoportail
public, pour comprendre ce qui existe avant de proposer des ameliorations.
"""
import re

chemin = "foncier/templates/foncier/geoportail.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

print("LONGUEUR TOTALE geoportail.html :", len(contenu), "caracteres")
print()

print("=" * 100)
print("1) Toutes les occurrences de 'voronoi' (positions + 60 caracteres de contexte)")
print("=" * 100)
for m in re.finditer(r"voronoi", contenu, re.IGNORECASE):
    idx = m.start()
    print(f"--- position {idx} ---")
    print(contenu[max(0, idx - 60): idx + 80].replace("\n", " \\n "))
print()

print("=" * 100)
print("2) Noms de fonctions JS contenant 'voronoi', 'desserte' ou 'desservie'")
print("=" * 100)
for m in re.finditer(r"function\s+(\w*(?:voronoi|desserte|desservie)\w*)\s*\(", contenu, re.IGNORECASE):
    print(m.group(1))
for m in re.finditer(r"(\w*(?:voronoi|desserte|desservie)\w*)\s*=\s*function\s*\(", contenu, re.IGNORECASE):
    print(m.group(1))
for m in re.finditer(r"(?:const|let|var)\s+(\w*(?:voronoi|desserte|desservie)\w*)\s*=", contenu, re.IGNORECASE):
    print(m.group(1))