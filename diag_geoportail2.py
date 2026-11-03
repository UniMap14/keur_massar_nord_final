# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_geoportail2.py', encoding='utf-8').read())"
"""
import inspect
import foncier.views as v

for nom in [
    "carte_geoportail", "carte_geoportail_admin",
    "api_parcelles_bounds",
    "api_parcelles_geojson", "api_parcelles_geojson_admin",
    "api_parcelles_toutes_geojson", "api_parcelles_toutes_geojson_admin",
    "api_zones_geojson",
]:
    fonction = getattr(v, nom, None)
    print("=" * 100)
    print(nom)
    print("=" * 100)
    if fonction is None:
        print("introuvable")
    else:
        try:
            print(inspect.getsource(fonction))
        except Exception as e:
            print("Erreur :", e)
    print()