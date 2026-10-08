CHEMIN_VIEWS = "foncier/views.py"
CHEMIN_URLS = "foncier/urls.py"

resultats = []

with open(CHEMIN_VIEWS, encoding="utf-8") as f:
    views = f.read()

ancre_vue = '''def cartotheque(request):
    """Page publique presentant les cartes thematiques d'analyse (MNT, pente, etc.)."""
    from .models import CarteThematique
    cartes = CarteThematique.objects.order_by('ordre', '-date_ajout')
    return render(request, 'foncier/cartotheque.html', {'cartes': cartes})'''

nouvelle_vue = '''


def foncier_info(request):
    """Page publique d'information sur le systeme foncier (documents, procedures, cadre legal)."""
    return render(request, 'foncier/foncier_info.html')'''

if "def foncier_info(request):" in views:
    resultats.append("views.py : IGNORE (deja present)")
elif ancre_vue in views:
    views = views.replace(ancre_vue, ancre_vue + nouvelle_vue, 1)
    with open(CHEMIN_VIEWS, "w", encoding="utf-8", newline="") as f:
        f.write(views)
    resultats.append("views.py : OK (vue foncier_info ajoutee)")
else:
    resultats.append("views.py : ERREUR ancre introuvable")

with open(CHEMIN_URLS, encoding="utf-8") as f:
    urls = f.read()

ancien_urls = "    path('cartotheque/', views.cartotheque, name='cartotheque'),"
nouveau_urls = ("    path('cartotheque/', views.cartotheque, name='cartotheque'),\n"
                "    path('foncier-info/', views.foncier_info, name='foncier_info'),")

if "name='foncier_info'" in urls:
    resultats.append("urls.py : IGNORE (deja present)")
elif ancien_urls in urls:
    urls = urls.replace(ancien_urls, nouveau_urls, 1)
    with open(CHEMIN_URLS, "w", encoding="utf-8", newline="") as f:
        f.write(urls)
    resultats.append("urls.py : OK (route ajoutee)")
else:
    resultats.append("urls.py : ERREUR ligne introuvable")

print("\n".join(resultats))