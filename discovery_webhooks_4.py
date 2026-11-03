# -*- coding: utf-8 -*-
import io, re, glob

print("=== Recherche de 'paiement_webhook_orange' dans tout le projet ===")
for chemin in glob.glob("**/*.py", recursive=True) + glob.glob("**/*.html", recursive=True):
    if "venv" in chemin.replace("\\", "/").split("/"):
        continue
    try:
        with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
            contenu = f.read()
    except Exception:
        continue
    if "paiement_webhook_orange" in contenu:
        for i, ligne in enumerate(contenu.splitlines(), start=1):
            if "paiement_webhook_orange" in ligne:
                print(f"{chemin}:{i}: {ligne.strip()}")

print("FIN")