# -*- coding: utf-8 -*-
import io, glob

print("=== Recherche de 'dashboard_password_reset_done/_confirm/_complete' dans tout le projet ===")
for chemin in glob.glob("**/*.py", recursive=True) + glob.glob("**/*.html", recursive=True):
    if "venv" in chemin.replace("\\", "/").split("/"):
        continue
    try:
        with io.open(chemin, "r", encoding="utf-8", errors="ignore") as f:
            contenu = f.read()
    except Exception:
        continue
    for mot in ["dashboard_password_reset_done", "dashboard_password_reset_confirm", "dashboard_password_reset_complete"]:
        if mot in contenu:
            for i, ligne in enumerate(contenu.splitlines(), start=1):
                if mot in ligne:
                    print(f"{chemin}:{i}: {ligne.strip()}")

print("FIN")