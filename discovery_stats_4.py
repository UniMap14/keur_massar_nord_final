# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/dashboard/home.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

print("=== Balise(s) <script> chargeant Chart.js ===")
for m in re.finditer(r"<script[^>]*chart[^>]*>", contenu, re.IGNORECASE):
    print(m.group(0))

print()
print("=== Premiere utilisation de 'new Chart(' (contexte, 40 lignes) ===")
lignes = contenu.splitlines()
for i, l in enumerate(lignes):
    if "new Chart(" in l:
        debut = max(0, i - 15)
        fin = min(len(lignes), i + 25)
        for j in range(debut, fin):
            print(f"{j+1}: {lignes[j]}")
        break