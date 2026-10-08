CHEMIN = "foncier/urls.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "    path('api/sections/', views.api_sections_geojson, name='api_sections'),"
nouveau = ("    path('api/sections/', views.api_sections_geojson, name='api_sections'),\n"
           "    path('api/limites/', views.api_limites_geojson, name='api_limites'),")

if "name='api_limites'" in contenu:
    print("DEJA FAIT : URL limites deja presente.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : URL api/limites/ ajoutee.")
else:
    print("ERREUR : ligne exacte introuvable.")