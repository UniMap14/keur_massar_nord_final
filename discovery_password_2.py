# -*- coding: utf-8 -*-
import io, re, glob

print("=== Contenu de foncier/permissions.py ===")
with io.open("foncier/permissions.py", "r", encoding="utf-8", errors="ignore") as f:
    print(f.read())

print()
print("=== Routes de connexion/login dans tous les urls.py ===")
for chemin in glob.glob("**/urls.py", recursive=True):
    if "venv" in chemin.replace("\\", "/").split("/"):
        continue
    with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
        contenu = f.read()
    for i, ligne in enumerate(contenu.splitlines(), start=1):
        if re.search(r"login|connexion", ligne, re.IGNORECASE):
            print(f"{chemin}:{i}: {ligne.strip()}")

print("FIN")