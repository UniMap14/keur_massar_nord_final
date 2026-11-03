# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/views.py"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

debuts = []
for i, l in enumerate(lignes):
    if re.search(r"def .*webhook.*\(", l, re.IGNORECASE):
        debuts.append(i)

for debut in debuts:
    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^def |^@", lignes[j]):
            fin = j
            break
    print(f"=== Fonction trouvee, lignes {debut+1}-{fin} ===")
    for i in range(debut, fin):
        print(lignes[i], end="")
    print()

print("=== Imports en haut de views.py lies a json/hmac/hashlib/settings ===")
for i, l in enumerate(lignes[:60]):
    if re.search(r"^import |^from ", l):
        print(f"{i+1}: {l}", end="")

print()
print("=== Variables liees a 'ORANGE' ou 'WAVE' dans kmsn/settings.py ===")
with io.open("kmsn/settings.py", "r", encoding="utf-8") as f:
    contenu_settings = f.read()
for ligne in contenu_settings.splitlines():
    if 'ORANGE' in ligne.upper() or 'WAVE' in ligne.upper():
        print(ligne)

print("FIN")