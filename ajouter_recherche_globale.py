CHEMIN_VIEWS = "foncier/views.py"
CHEMIN_URLS = "foncier/urls.py"

resultats = []

with open(CHEMIN_VIEWS, encoding="utf-8") as f:
    views = f.read()

ancre_vue = '''def foncier_info(request):
    """Page publique d'information sur le systeme foncier (documents, procedures, cadre legal)."""
    return render(request, 'foncier/foncier_info.html')'''

nouvelle_vue = '''


def recherche_globale(request):
    """Recherche simple sur le site : actualites et cartotheque."""
    from django.db.models import Q
    from .models import Actualite, CarteThematique

    requete = request.GET.get('q', '').strip()
    actualites_trouvees = []
    cartes_trouvees = []

    if requete:
        actualites_trouvees = Actualite.objects.filter(
            Q(titre__icontains=requete) | Q(chapo__icontains=requete)
        ).order_by('-date_publication')[:20]

        cartes_trouvees = CarteThematique.objects.filter(
            Q(titre__icontains=requete) | Q(explication__icontains=requete)
        ).order_by('ordre')[:20]

    total = len(actualites_trouvees) + len(cartes_trouvees)

    return render(request, 'foncier/recherche_globale.html', {
        'q': requete,
        'actualites_trouvees': actualites_trouvees,
        'cartes_trouvees': cartes_trouvees,
        'total': total,
    })'''

if "def recherche_globale(request):" in views:
    resultats.append("views.py : IGNORE (deja present)")
elif ancre_vue in views:
    views = views.replace(ancre_vue, ancre_vue + nouvelle_vue, 1)
    with open(CHEMIN_VIEWS, "w", encoding="utf-8", newline="") as f:
        f.write(views)
    resultats.append("views.py : OK (vue recherche_globale ajoutee)")
else:
    resultats.append("views.py : ERREUR ancre introuvable")

with open(CHEMIN_URLS, encoding="utf-8") as f:
    urls = f.read()

ancien_urls = "    path('foncier-info/', views.foncier_info, name='foncier_info'),"
nouveau_urls = ("    path('foncier-info/', views.foncier_info, name='foncier_info'),\n"
                "    path('recherche/', views.recherche_globale, name='recherche_globale'),")

if "name='recherche_globale'" in urls:
    resultats.append("urls.py : IGNORE (deja present)")
elif ancien_urls in urls:
    urls = urls.replace(ancien_urls, nouveau_urls, 1)
    with open(CHEMIN_URLS, "w", encoding="utf-8", newline="") as f:
        f.write(urls)
    resultats.append("urls.py : OK (route ajoutee)")
else:
    resultats.append("urls.py : ERREUR ligne introuvable")

print("\n".join(resultats))