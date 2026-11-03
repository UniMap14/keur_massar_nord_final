# -*- coding: utf-8 -*-
import io, re

with io.open("foncier/paiement_gateway.py", "r", encoding="utf-8") as f:
    contenu = f.read()

print("=== Lignes contenant 'import' dans les 60 premieres lignes ===")
for i, ligne in enumerate(contenu.splitlines()[:60], start=1):
    if re.match(r"^\s*(import|from)\s", ligne):
        print(f"{i}: {ligne}")