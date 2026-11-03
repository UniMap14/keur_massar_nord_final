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

for pattern in [r"class CitoyenLoginView", r"def otp_verify_view", r"def otp_resend_view"]:
    debut, fin = extraire_fonction(pattern, lignes)
    if debut is not None:
        print(f"=== {pattern} : lignes {debut+1}-{fin} ===")
        for i in range(debut, fin):
            print(lignes[i], end="")
        print()
    else:
        print(f"=== {pattern} : NON TROUVE ===")

print("FIN")