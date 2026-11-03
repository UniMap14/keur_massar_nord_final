# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== foncier/dashboard_urls.py lignes 1-55 ===")
with io.open("foncier/dashboard_urls.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()
print("".join(lignes[:55]))

print()
print("=== kmsn/urls.py (pour voir l'inclusion de dashboard_urls, prefixe gestion/) ===")
with io.open("kmsn/urls.py", "r", encoding="utf-8") as f:
    print(f.read())