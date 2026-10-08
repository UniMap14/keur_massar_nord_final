CHEMIN = "foncier/urls.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "    path('api/zones/', views.api_zones_geojson, name='api_zones'),"
nouveau = ("    path('api/zones/', views.api_zones_geojson, name='api_zones'),\n"
           "    path('api/sections/', views.api_sections_geojson, name='api_sections'),")

if "name='api_sections'" in contenu:
    print("DEJA FAIT : URL sections deja presente.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : URL api/sections/ ajoutee.")
else:
    print("ERREUR : ligne exacte introuvable.")