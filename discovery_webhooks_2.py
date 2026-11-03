# -*- coding: utf-8 -*-
import io, re

with io.open("foncier/urls.py", "r", encoding="utf-8") as f:
    contenu = f.read()

print("=== Lignes de urls.py liees aux webhooks de paiement ===")
for i, ligne in enumerate(contenu.splitlines(), start=1):
    if 'webhook' in ligne.lower():
        print(f"{i}: {ligne}")