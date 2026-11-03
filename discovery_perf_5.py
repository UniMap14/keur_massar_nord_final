# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/views.py"
with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()
    lignes = contenu.splitlines()

print("=== Contexte autour de '_invalider_cache_parcelles' (signal) ===")
for i, l in enumerate(lignes):
    if "_invalider_cache_parcelles" in l or "@receiver" in l:
        print(f"{i+1}: {l}")

print()
print("=== Bloc complet du/des signal(s) (recherche large 'receiver' a 'post_save'/'post_delete') ===")
m = re.search(r"(@receiver.*?_invalider_cache_parcelles\([^)]*\):\n(?:.*\n)*?(?=\n\n|\Z))", contenu, re.MULTILINE)
if m:
    print(m.group(1))
else:
    for i, l in enumerate(lignes):
        if "_invalider_cache_parcelles" in l and "def " in l:
            for j in range(max(0, i-5), min(len(lignes), i+15)):
                print(f"{j+1}: {lignes[j]}")
            break

print()
print("=== imports en haut du fichier ===")
for i, l in enumerate(lignes[:60]):
    print(f"{i+1}: {l}")