# -*- coding: utf-8 -*-
import sys, io, re, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("=== Recherche de 'chart.js' / 'Chart.js' / 'new Chart(' dans tout le projet (hors venv) ===")
for ext in ("*.html", "*.js"):
    for chemin in glob.glob(f"**/{ext}", recursive=True):
        if "venv" in chemin.replace("\\", "/").split("/"):
            continue
        try:
            with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                contenu = f.read()
        except Exception:
            continue
        if re.search(r"chart\.js|new Chart\(|Chart\.register", contenu, re.IGNORECASE):
            print(chemin)

print()
print("=== base.html : scripts/CSS charges (balises <script> et <link>) ===")
chemin_base = "foncier/templates/foncier/base.html"
if os.path.exists(chemin_base):
    with io.open(chemin_base, "r", encoding="utf-8") as f:
        contenu_base = f.read()
    for m in re.finditer(r"<script[^>]*>|<link[^>]*>", contenu_base):
        print(m.group(0))
else:
    print("base.html introuvable a ce chemin, recherche large :")
    for c in glob.glob("**/base.html", recursive=True):
        print(c)