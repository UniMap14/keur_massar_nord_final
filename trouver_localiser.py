# -*- coding: utf-8 -*-
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

racine = os.getcwd()
motif = re.compile(r"localiser|geolocation|getCurrentPosition", re.IGNORECASE)

print("=== Fichiers contenant 'localiser'/'geolocation'/'getCurrentPosition' ===")
for base, dirs, files in os.walk(racine):
    if 'venv' in base or '.git' in base or 'node_modules' in base or '__pycache__' in base:
        continue
    for f in files:
        if f.endswith((".py", ".html", ".js")):
            chemin = os.path.join(base, f)
            try:
                with io.open(chemin, "r", encoding="utf-8", errors="replace") as fp:
                    contenu = fp.read()
            except Exception:
                continue
            if motif.search(contenu):
                rel = os.path.relpath(chemin, racine)
                nb = len(motif.findall(contenu))
                print(f"{rel}  ({nb} occurrence(s))")