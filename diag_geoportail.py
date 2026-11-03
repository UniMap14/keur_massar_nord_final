# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_geoportail.py', encoding='utf-8').read())"

Objectif : comprendre pourquoi le geoportail (public + admin) est lent
a charger : combien de features sont envoyees, avec quelle precision
geometrique, est-ce mis en cache, etc.
"""
import inspect
import time
import os

print("=" * 100)
print("1) Fichiers contenant 'api_parcelles' ou 'api_zones' ou 'geoportail'")
print("=" * 100)
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in (
        ".venv", "venv", "env", ".git", "node_modules", "__pycache__", "staticfiles"
    )]
    for f in filenames:
        if f.endswith(".py"):
            chemin = os.path.join(dirpath, f)
            try:
                with open(chemin, "r", encoding="utf-8", errors="replace") as fh:
                    contenu = fh.read()
            except Exception:
                continue
            if "def api_parcelles" in contenu or "def api_zones" in contenu or "def geoportail" in contenu:
                print(chemin)
print()

import foncier.views as v
print("=" * 100)
print("2) Fonctions candidates trouvees dans foncier.views")
print("=" * 100)
for nom in dir(v):
    if "geoportail" in nom.lower() or "api_parcelle" in nom.lower() or "api_zone" in nom.lower() or "api_infra" in nom.lower():
        print(nom)
print()

for nom in ["api_parcelles", "api_zones", "api_infrastructures", "geoportail"]:
    fonction = getattr(v, nom, None)
    if fonction is None:
        continue
    print("=" * 100)
    print(f"3) Code de {nom}")
    print("=" * 100)
    try:
        print(inspect.getsource(fonction))
    except Exception as e:
        print("Erreur :", e)
    print()

print("=" * 100)
print("4) Mesure reelle : taille/temps de la reponse GeoJSON des parcelles")
print("=" * 100)
try:
    from foncier.models import Parcelle
    t0 = time.time()
    nb = Parcelle.objects.count()
    t1 = time.time()
    print(f"Nombre de parcelles : {nb} (count: {t1-t0:.3f}s)")

    from django.test import Client
    client = Client()
    t0 = time.time()
    resp = client.get("/api/parcelles/") if True else None
except Exception as e:
    print("Tentative d'appel direct impossible ici, pas grave :", e)