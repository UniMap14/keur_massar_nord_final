# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/base.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

print("=== Tous les '{% block ... %}' dans foncier/base.html ===")
for m in re.finditer(r"\{%\s*block\s+\w+\s*%\}", contenu):
    print(m.group(0))

print()
print("=== Fin du fichier (30 dernieres lignes, pour voir ou placer les scripts) ===")
lignes = contenu.splitlines()
for l in lignes[-30:]:
    print(l)