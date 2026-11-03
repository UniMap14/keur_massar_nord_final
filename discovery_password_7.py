# -*- coding: utf-8 -*-
import io, re, glob

with io.open("foncier/dashboard_views.py", "r", encoding="utf-8") as f:
    contenu = f.read()
    lignes = contenu.splitlines(keepends=True)

debut = None
for i, l in enumerate(lignes):
    if "MOT DE PASSE OUBLIÉ" in l:
        debut = i
        break

fin = len(lignes)
if debut is not None:
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^def dashboard_home", lignes[j]) or re.match(r"^# ====", lignes[j]) and j > debut + 10:
            fin = j
            break
    print(f"=== Bloc mot de passe oublie, lignes {debut+1} a {fin} ===")
    for i in range(debut, min(fin, debut + 250)):
        print(lignes[i], end="")

print()
print("=== Imports en tete de dashboard_views.py (50 premieres lignes) ===")
for i, l in enumerate(lignes[:50]):
    print(f"{i+1}: {l}", end="")

print()
print("=== Fichiers dans templates/registration/ ===")
for chemin in glob.glob("foncier/templates/registration/*.html"):
    print(chemin)

print("FIN")