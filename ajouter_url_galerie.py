CHEMIN = "foncier/urls.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "    path('signalement/', views.signalement, name='signalement'),"
nouveau = ("    path('galerie/', views.galerie, name='galerie'),\n"
           "    path('signalement/', views.signalement, name='signalement'),")

if "name='galerie'" in contenu:
    print("DEJA FAIT : URL 'galerie' deja presente.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : URL 'galerie/' ajoutee.")
else:
    print("ERREUR : ligne exacte introuvable.")