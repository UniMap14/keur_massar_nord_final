# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_infra_form_html.py', encoding='utf-8').read())"
"""
import os

for chemin in [
    "foncier/templates/dashboard/infrastructure_form.html",
]:
    print("=" * 100)
    print(chemin, "-> existe :", os.path.exists(chemin))
    print("=" * 100)
    if os.path.exists(chemin):
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            contenu = f.read()
            print(contenu)
            print()
            print("=" * 100)
            print("LONGUEUR :", len(contenu), "caracteres")
    print()

print("=" * 100)
print("Verif existence API zones/parcelles (pour reference eventuelle)")
print("=" * 100)
import subprocess
try:
    out = subprocess.run(["grep", "-n", "api_zones\\|api_parcelles", "foncier/dashboard_urls.py"],
                          capture_output=True, text=True)
    print(out.stdout)
except Exception as e:
    print("Erreur grep :", e)