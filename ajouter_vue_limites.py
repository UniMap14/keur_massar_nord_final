CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''def api_sections_geojson(request):
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

nouveau = '''def api_sections_geojson(request):
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

    return JsonResponse({"type": "FeatureCollection", "features": features})


def api_limites_geojson(request):
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

if "def api_limites_geojson" in contenu:
    print("DEJA FAIT : vue deja presente.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : vue api_limites_geojson ajoutee.")
else:
    print("ERREUR : bloc exact introuvable.")