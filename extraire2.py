# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
chemin = sys.argv[1]
debut = int(sys.argv[2])
fin = int(sys.argv[3])
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()
print("".join(lignes[debut-1:fin]))