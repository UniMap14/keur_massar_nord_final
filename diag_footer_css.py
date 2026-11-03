# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_footer_css.py', encoding='utf-8').read())"
"""
import re

chemin = "foncier/static/foncier/css/style.css"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

print("LONGUEUR TOTALE :", len(contenu), "caracteres")
print()

# Trouver tous les indices ou "footer" apparait, et afficher le bloc CSS autour
indices = [m.start() for m in re.finditer(r"footer", contenu, re.IGNORECASE)]
print("Nombre d'occurrences de 'footer' :", len(indices))
print()

deja_vus = set()
for idx in indices:
    debut = max(0, idx - 60)
    fin = min(len(contenu), idx + 400)
    bloc = contenu[debut:fin]
    cle = bloc[:50]
    if cle in deja_vus:
        continue
    deja_vus.add(cle)
    print("-" * 100)
    print(f"(position {idx})")
    print(bloc)
    print()