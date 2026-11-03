# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_geoportail_perf.py', encoding='utf-8').read())"
"""
import time
from django.core.cache import cache
from django.conf import settings

print("=" * 100)
print("1) Backend de cache configure (settings.CACHES)")
print("=" * 100)
print(getattr(settings, "CACHES", "non defini (cache par defaut = LocMemCache)"))
print()

import foncier.views as v

print("=" * 100)
print("2) Cle de cache utilisee, deja en cache ou pas ?")
print("=" * 100)
print("CACHE_KEY_PUBLIC present :", cache.get(v.CACHE_KEY_PUBLIC) is not None)
print("CACHE_KEY_ADMIN present  :", cache.get(v.CACHE_KEY_ADMIN) is not None)
print("CACHE_KEY_ZONES present  :", cache.get(v.CACHE_KEY_ZONES) is not None)
print()

print("=" * 100)
print("3) Tolerances de simplification configurees")
print("=" * 100)
print("TOLERANCE_SIMPLIFICATION        :", v.TOLERANCE_SIMPLIFICATION)
print("TOLERANCE_SIMPLIFICATION_TOUTES :", v.TOLERANCE_SIMPLIFICATION_TOUTES)
print("PARCELLES_MAX_PAR_REQUETE       :", v.PARCELLES_MAX_PAR_REQUETE)
print()

print("=" * 100)
print("4) Temps reel de calcul 'a froid' de api_parcelles_toutes_geojson (cache vide)")
print("=" * 100)
cache.delete(v.CACHE_KEY_PUBLIC)
from django.test import RequestFactory
rf = RequestFactory()
req = rf.get("/api/parcelles-toutes/")

t0 = time.time()
resp = v.api_parcelles_toutes_geojson(req)
t1 = time.time()
print(f"Premier appel (cache vide) : {t1 - t0:.3f}s -- taille reponse : {len(resp.content)} octets")

t0 = time.time()
resp2 = v.api_parcelles_toutes_geojson(req)
t1 = time.time()
print(f"Deuxieme appel (cache chaud) : {t1 - t0:.3f}s")
print()

print("=" * 100)
print("5) Nombre de features renvoyees par 'toutes' (vue d'ensemble dezoomee)")
print("=" * 100)
import json
data = json.loads(resp.content)
print("Nombre de parcelles dans la reponse :", len(data.get("features", [])))