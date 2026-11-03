# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Contexte lignes 2035-2060 (fonction utilisant allLimites + booleanPointInPolygon) ===")
print("".join(lignes[2034:2060]))

print()
print("=== Contexte lignes 2110-2130 (filtreInfraCategorie / infrastructuresFiltrees) ===")
print("".join(lignes[2109:2130]))