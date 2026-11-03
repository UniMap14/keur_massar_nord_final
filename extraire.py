# -*- coding: utf-8 -*-
"""
Usage : python extraire.py <chemin_fichier> <nom1> [nom2] [nom3] ...
Affiche le code complet de chaque fonction/classe nommee (du "def x(" ou
"class X" jusqu'a la ligne precedant la prochaine def/class de meme
niveau d'indentation), sans jamais tronquer. Insensible aux accents
dans le nom cherche (ex: "Proprietaire" matche aussi "Propriétaire").
"""
import sys
import io
import re
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def sans_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

chemin = sys.argv[1]
noms = sys.argv[2:]

with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

lignes_norm = [sans_accents(l) for l in lignes]

for nom in noms:
    nom_norm = sans_accents(nom)
    motif = re.compile(r"^(def|class)\s+" + re.escape(nom_norm) + r"\b")
    debut = None
    for i, ligne in enumerate(lignes_norm):
        if motif.match(ligne):
            debut = i
            break
    if debut is None:
        print(f"\n=== {nom} : INTROUVABLE ===\n")
        continue
    fin = len(lignes)
    for j in range(debut + 1, len(lignes_norm)):
        if re.match(r"^(def|class)\s+\w", lignes_norm[j]):
            fin = j
            break
    print(f"\n=== {nom} (lignes {debut+1}-{fin}) ===")
    print("".join(lignes[debut:fin]))