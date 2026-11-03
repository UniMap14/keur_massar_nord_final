# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with io.open("foncier/urls.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

print("=== Lignes contenant 'dashboard_parcelle_list' ou 'gestion/' (pour voir le pattern des URLs dashboard) ===")
for i, l in enumerate(lignes, 1):
    if re.search(r"dashboard_parcelle_list|dashboard_contribuable_list|dashboard_home", l):
        print(f"{i}: {l.rstrip()}")

print()
print("=== 20 premieres lignes de foncier/urls.py (imports / debut) ===")
print("".join(lignes[:20]))