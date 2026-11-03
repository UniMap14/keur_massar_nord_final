# -*- coding: utf-8 -*-
import io, re

with io.open("foncier/dashboard_views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

debut = None
for i, l in enumerate(lignes):
    if re.search(r"class DashboardLoginView", l):
        debut = i
        break
fin = len(lignes)
if debut is not None:
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^class |^def |^@", lignes[j]):
            fin = j
            break
    print(f"=== DashboardLoginView : lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(lignes[i], end="")

print()
print("=== foncier/dashboard_urls.py (complet) ===")
with io.open("foncier/dashboard_urls.py", "r", encoding="utf-8") as f:
    print(f.read())

print()
print("=== foncier/templates/dashboard/login.html (complet) ===")
with io.open("foncier/templates/dashboard/login.html", "r", encoding="utf-8") as f:
    print(f.read())

print("FIN")