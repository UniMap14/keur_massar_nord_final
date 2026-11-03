# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_sidebar_css.py', encoding='utf-8').read())"

Objectif : localiser le CSS de la sidebar du dashboard admin (fond brun
fonce visible sur la capture d'ecran), pour y appliquer le meme degrade
dore/marron que le footer du site public.
"""
import re

chemin = "foncier/static/dashboard/css/dashboard.css"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

print("LONGUEUR TOTALE :", len(contenu), "caracteres")
print()

print("=" * 100)
print(":root (variables de couleur)")
print("=" * 100)
m = re.search(r":root\s*\{[^}]*\}", contenu, re.DOTALL)
print(m.group(0) if m else "introuvable")
print()

print("=" * 100)
print("Selecteurs contenant 'sidebar' (nom + premieres lignes de chaque regle)")
print("=" * 100)
for m in re.finditer(r"([^\{\}]*sidebar[^\{\}]*)\{([^\}]*)\}", contenu, re.IGNORECASE):
    selecteur = m.group(1).strip()
    corps = m.group(2).strip()
    print(f"--- {selecteur} ---")
    print(corps[:400])
    print()