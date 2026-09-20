CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

def api_parcelles_bounds(request):
    """
    Renvoie l'enveloppe geographique (bounding box) de TOUTES les
    parcelles, calculee cote base de donnees (tres rapide, une seule
    requete d'agregation). Utilisee par la carte pour se cadrer
    automatiquement sur tout le territoire des l'ouverture, quelle que
    soit la taille de l'ecran -- garantit qu'on ne "rate" jamais une
    partie de la commune au chargement initial.
    """
    from django.contrib.gis.db.models import Extent

    resultat = Parcelle.objects.exclude(geom__isnull=True).aggregate(etendue=Extent("geom"))
    etendue = resultat["etendue"]
    if not etendue:
        return JsonResponse({"ok": False})
    west, south, east, north = etendue
    return JsonResponse({"ok": True, "west": west, "south": south, "east": east, "north": north})
'''

if "def api_parcelles_bounds" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : vue api_parcelles_bounds ajoutee a la fin du fichier.")