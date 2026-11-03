# -*- coding: utf-8 -*-
import io, re, glob

print("=== Recherche de 'password_reset' ou 'mot_de_passe_oublie' dans urls.py (tous) ===")
for chemin in glob.glob("**/urls.py", recursive=True):
    if "venv" in chemin.replace("\\", "/").split("/"):
        continue
    with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
        contenu = f.read()
    for i, ligne in enumerate(contenu.splitlines(), start=1):
        if re.search(r"password.?reset|mot.?de.?passe", ligne, re.IGNORECASE):
            print(f"{chemin}:{i}: {ligne.strip()}")

print()
print("=== Configuration EMAIL dans kmsn/settings.py ===")
with io.open("kmsn/settings.py", "r", encoding="utf-8") as f:
    contenu_settings = f.read()
for ligne in contenu_settings.splitlines():
    if "EMAIL" in ligne.upper():
        print(ligne)

print()
print("=== Fonctions liees a 'password' ou 'code' dans foncier/views.py ===")
with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    contenu_views = f.read()
for i, ligne in enumerate(contenu_views.splitlines(), start=1):
    if re.search(r"def .*(password|motdepasse|mot_de_passe|reset|code_verif)", ligne, re.IGNORECASE):
        print(f"{i}: {ligne.strip()}")

print("FIN")