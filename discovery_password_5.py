# -*- coding: utf-8 -*-
import io, re, glob

print("=== Recherche de 'dashboard/login.html' dans tout le projet ===")
for chemin in glob.glob("**/*.py", recursive=True):
    if "venv" in chemin.replace("\\", "/").split("/"):
        continue
    with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
        contenu = f.read()
    for i, ligne in enumerate(contenu.splitlines(), start=1):
        if "dashboard/login.html" in ligne or "LoginView" in ligne:
            print(f"{chemin}:{i}: {ligne.strip()}")

print()
print("=== Routes contenant 'gestion' ou 'dashboard' dans foncier/urls.py ===")
with io.open("foncier/urls.py", "r", encoding="utf-8", errors="ignore") as f:
    contenu = f.read()
for i, ligne in enumerate(contenu.splitlines(), start=1):
    if re.search(r"login|connexion|dashboard_login", ligne, re.IGNORECASE):
        print(f"{i}: {ligne.strip()}")

print("FIN")