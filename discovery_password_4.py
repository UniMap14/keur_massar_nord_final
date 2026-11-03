# -*- coding: utf-8 -*-
import io, re

with io.open("citoyens/views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()

def extraire_fonction(nom_pattern, lignes):
    debut = None
    for i, l in enumerate(lignes):
        if re.search(nom_pattern, l):
            debut = i
            break
    if debut is None:
        return None, None
    fin = len(lignes)
    for j in range(debut + 1, len(lignes)):
        if re.match(r"^def |^class |^@", lignes[j]):
            fin = j
            break
    return debut, fin

for pattern in [r"def _generer_otp", r"def _envoyer_otp"]:
    debut, fin = extraire_fonction(pattern, lignes)
    if debut is not None:
        print(f"=== {pattern} : lignes {debut+1}-{fin} ===")
        for i in range(debut, fin):
            print(lignes[i], end="")
        print()
    else:
        print(f"=== {pattern} : NON TROUVE ===")

print()
print("=== Contenu complet de comptes/views.py ===")
with io.open("comptes/views.py", "r", encoding="utf-8", errors="ignore") as f:
    print(f.read())

print()
print("=== Contenu complet de comptes/urls.py ===")
with io.open("comptes/urls.py", "r", encoding="utf-8", errors="ignore") as f:
    print(f.read())

print("FIN")