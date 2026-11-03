# -*- coding: utf-8 -*-
"""
Optimisation performance : mise en cache (indefinie, comme pour les
parcelles) des couches Zones/Quartiers, Sections cadastrales et Limites
administratives. Ces 3 couches sont actuellement recalculees depuis la
base ET re-serialisees en JSON a CHAQUE chargement des deux geoportails
(public et admin), alors qu'elles changent tres rarement.

Idempotent.
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "CACHE_KEY_ZONES"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Nouvelles cles de cache ---
    ancien_cles = '''CACHE_KEY_PUBLIC = "geojson_parcelles_public"
CACHE_KEY_ADMIN = "geojson_parcelles_admin"
CACHE_TTL_SECONDES = 120  # invalidé de toute façon dès qu'une parcelle est modifiée'''
    if ancien_cles not in contenu:
        raise SystemExit("ANCRE cles de cache INTROUVABLE - abandon, rien n'a ete modifie.")
    nouveau_cles = '''CACHE_KEY_PUBLIC = "geojson_parcelles_public"
CACHE_KEY_ADMIN = "geojson_parcelles_admin"
CACHE_TTL_SECONDES = 120  # invalidé de toute façon dès qu'une parcelle est modifiée
CACHE_KEY_ZONES = "geojson_zones"
CACHE_KEY_SECTIONS = "geojson_sections"
CACHE_KEY_LIMITES = "geojson_limites"'''
    contenu = contenu.replace(ancien_cles, nouveau_cles)

    # --- 2) api_zones_geojson : mise en cache ---
    ancien_zones = '''def api_zones_geojson(request):
    """
    Calque "Zones/Quartiers" : quartiers officiels importes dans le
    modele QuartierOfficiel (remplace l'ancienne requete SQL brute sur
    la table temporaire kmsn_quartier).
    """
    from foncier.models import QuartierOfficiel

    features = [
        {
            "type": "Feature",
            "geometry": json.loads(q.geom.geojson),
            "properties": {"nom": q.nom},
        }
        for q in QuartierOfficiel.objects.all()
    ]

    return JsonResponse({"type": "FeatureCollection", "features": features})'''
    if ancien_zones not in contenu:
        raise SystemExit("ANCRE api_zones_geojson INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_zones = '''def api_zones_geojson(request):
    """
    Calque "Zones/Quartiers" : quartiers officiels importes dans le
    modele QuartierOfficiel (remplace l'ancienne requete SQL brute sur
    la table temporaire kmsn_quartier).
    Mis en cache indéfiniment (invalidé par le signal
    _invalider_cache_zones) : ces quartiers changent tres rarement, pas
    la peine de refaire le tour de la table a chaque chargement de la
    carte, sur les deux geoportails.
    """
    data = cache.get(CACHE_KEY_ZONES)
    if data is None:
        from foncier.models import QuartierOfficiel

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(q.geom.geojson),
                "properties": {"nom": q.nom},
            }
            for q in QuartierOfficiel.objects.all()
        ]
        data = json.dumps({"type": "FeatureCollection", "features": features})
        cache.set(CACHE_KEY_ZONES, data, None)

    return HttpResponse(data, content_type="application/json")'''
    contenu = contenu.replace(ancien_zones, nouveau_zones)

    # --- 3) api_sections_geojson : mise en cache ---
    ancien_sections = '''def api_sections_geojson(request):
    """Calque "Sections cadastrales" : sections officielles importees."""
    from foncier.models import SectionCadastrale

    features = [
        {
            "type": "Feature",
            "geometry": json.loads(s.geom.geojson),
            "properties": {"numero": s.numero},
        }
        for s in SectionCadastrale.objects.all()
    ]

    return JsonResponse({"type": "FeatureCollection", "features": features})'''
    if ancien_sections not in contenu:
        raise SystemExit("ANCRE api_sections_geojson INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_sections = '''def api_sections_geojson(request):
    """Calque "Sections cadastrales" : sections officielles importees.
    Mis en cache indéfiniment (invalidé par le signal
    _invalider_cache_sections)."""
    data = cache.get(CACHE_KEY_SECTIONS)
    if data is None:
        from foncier.models import SectionCadastrale

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(s.geom.geojson),
                "properties": {"numero": s.numero},
            }
            for s in SectionCadastrale.objects.all()
        ]
        data = json.dumps({"type": "FeatureCollection", "features": features})
        cache.set(CACHE_KEY_SECTIONS, data, None)

    return HttpResponse(data, content_type="application/json")'''
    contenu = contenu.replace(ancien_sections, nouveau_sections)

    # --- 4) api_limites_geojson : mise en cache ---
    ancien_limites = '''def api_limites_geojson(request):
    """Calque "Limites administratives" : limite(s) officielle(s) de la commune."""
    from foncier.models import LimiteAdministrative

    features = [
        {
            "type": "Feature",
            "geometry": json.loads(l.geom.geojson),
            "properties": {"nom": l.nom},
        }
        for l in LimiteAdministrative.objects.all()
    ]

    return JsonResponse({"type": "FeatureCollection", "features": features})'''
    if ancien_limites not in contenu:
        raise SystemExit("ANCRE api_limites_geojson INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_limites = '''def api_limites_geojson(request):
    """Calque "Limites administratives" : limite(s) officielle(s) de la
    commune. Mis en cache indéfiniment (invalidé par le signal
    _invalider_cache_limites)."""
    data = cache.get(CACHE_KEY_LIMITES)
    if data is None:
        from foncier.models import LimiteAdministrative

        features = [
            {
                "type": "Feature",
                "geometry": json.loads(l.geom.geojson),
                "properties": {"nom": l.nom},
            }
            for l in LimiteAdministrative.objects.all()
        ]
        data = json.dumps({"type": "FeatureCollection", "features": features})
        cache.set(CACHE_KEY_LIMITES, data, None)

    return HttpResponse(data, content_type="application/json")'''
    contenu = contenu.replace(ancien_limites, nouveau_limites)

    # --- 5) Signaux d'invalidation, juste apres celui des parcelles ---
    ancien_signal = '''@receiver([post_save, post_delete], sender=Parcelle)
def _invalider_cache_parcelles(sender, **kwargs):
    cache.delete(CACHE_KEY_PUBLIC)
    cache.delete(CACHE_KEY_ADMIN)'''
    if ancien_signal not in contenu:
        raise SystemExit("ANCRE signal _invalider_cache_parcelles INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_signal = '''@receiver([post_save, post_delete], sender=Parcelle)
def _invalider_cache_parcelles(sender, **kwargs):
    cache.delete(CACHE_KEY_PUBLIC)
    cache.delete(CACHE_KEY_ADMIN)


from foncier.models import QuartierOfficiel, SectionCadastrale, LimiteAdministrative


@receiver([post_save, post_delete], sender=QuartierOfficiel)
def _invalider_cache_zones(sender, **kwargs):
    cache.delete(CACHE_KEY_ZONES)


@receiver([post_save, post_delete], sender=SectionCadastrale)
def _invalider_cache_sections(sender, **kwargs):
    cache.delete(CACHE_KEY_SECTIONS)


@receiver([post_save, post_delete], sender=LimiteAdministrative)
def _invalider_cache_limites(sender, **kwargs):
    cache.delete(CACHE_KEY_LIMITES)'''
    contenu = contenu.replace(ancien_signal, nouveau_signal)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes (cache zones/sections/limites).")