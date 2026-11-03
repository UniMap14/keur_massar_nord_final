# -*- coding: utf-8 -*-
import sys, io, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== urls.py : route 'statistiques' ===")
with io.open("foncier/urls.py", "r", encoding="utf-8") as f:
    contenu_urls = f.read()
for ligne in contenu_urls.splitlines():
    if "statistique" in ligne.lower():
        print(ligne)

print()
print("=== views.py : fonction(s) liees a 'statistique' ===")
with io.open("foncier/views.py", "r", encoding="utf-8") as f:
    lignes = f.readlines()
for i, l in enumerate(lignes):
    if re.search(r"def .*statistique.*\(", l, re.IGNORECASE):
        print(f"{i+1}: {l.rstrip()}")

print()
print("=== Recherche du template statistiques ===")
candidats = glob.glob("**/*statistique*.html", recursive=True)
for c in candidats:
    print(c, ":", os.path.getsize(c), "octets")