CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''def api_zones_geojson(request):
    """
    Version temporaire : affiche les quartiers depuis la table
    'kmsn_quartier' (nom du quartier via QRT_VLG_HA), si elle a été
    importée. Si elle n'existe pas encore (aucun shapefile de quartiers
    importé), on renvoie simplement une liste vide plutôt que de faire
    planter la carte : les parcelles doivent pouvoir s'afficher même
    sans ce calque de zones.
    """
    from django.db.utils import ProgrammingError

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    "QRT_VLG_HA" AS nom,
                    ST_AsGeoJSON(ST_Transform(geom, 4326)) AS geometry
                FROM kmsn_quartier
            """)
            rows = cursor.fetchall()
    except ProgrammingError:
        # Table absente : pas encore de shapefile de quartiers importé.
        connection.rollback()
        rows = []

    features = [
        {
            "type": "Feature",
            "geometry": json.loads(geometry),
            "properties": {
                "nom": nom,
            },
        }
        for nom, geometry in rows
    ]

    return JsonResponse({"type": "FeatureCollection", "features": features})'''

nouveau = '''def api_zones_geojson(request):
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

    return JsonResponse({"type": "FeatureCollection", "features": features})


def api_sections_geojson(request):
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

if "def api_sections_geojson" in contenu:
    print("DEJA FAIT : vues deja presentes.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : api_zones_geojson nettoyee (utilise QuartierOfficiel), api_sections_geojson ajoutee.")
else:
    print("ERREUR : bloc exact introuvable.")