# -*- coding: utf-8 -*-
"""
Supprime completement la page Infrastructures :
- la vue dans foncier/views.py
- l'URL dans foncier/urls.py
- le lien dans le menu (foncier/templates/foncier/base.html)
- la tuile dans la page d'accueil (foncier/templates/foncier/home.html)
"""

resultats = []


def remplacer(chemin, ancien, description, obligatoire=True):
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()
    if ancien not in contenu:
        resultats.append(f"IGNORE : {description} (deja absent ou introuvable)")
        return
    contenu = contenu.replace(ancien, "", 1)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    resultats.append(f"OK : {description}")


# 1. La vue dans views.py
remplacer(
    "foncier/views.py",
    '''def infrastructures(request):
    """
    Page publique des infrastructures : chiffres clés par catégorie,
    détail par catégorie (liste réelle des équipements), avec une
    recherche/filtre facultatif par nom, quartier ou catégorie.
    """

    q = request.GET.get('q', '').strip()
    categorie_code = request.GET.get('categorie', '').strip()

    infra_qs = Infrastructure.objects.all().order_by('nom')

    if q:
        infra_qs = infra_qs.filter(
            Q(nom__icontains=q) | Q(quartier__icontains=q)
        )

    if categorie_code:
        infra_qs = infra_qs.filter(categorie__code=categorie_code)

    categories = (
        CategorieInfrastructure.objects
        .annotate(total_infra=Count('infrastructures', distinct=True))
        .prefetch_related(
            Prefetch('infrastructures', queryset=infra_qs, to_attr='infrastructures_filtrees')
        )
        .order_by('ordre', 'label')
    )

    # Pour la grille "chiffres clés" en haut de page : on garde le total
    # RÉEL par catégorie (pas filtré par la recherche), pour ne pas fausser
    # les statistiques globales même quand l'utilisateur filtre la liste.
    chiffres_cles = (
        CategorieInfrastructure.objects
        .annotate(total=Count('infrastructures', distinct=True))
        .order_by('ordre', 'label')
    )

    # Liste des catégories pour le menu déroulant du filtre
    toutes_categories = CategorieInfrastructure.objects.order_by('ordre', 'label')

    context = {
        'infrastructures': chiffres_cles,   # utilisé par la grille de chiffres clés
        'categories': categories,           # utilisé par les panneaux détaillés
        'toutes_categories': toutes_categories,
        'q': q,
        'categorie_code': categorie_code,
    }
    return render(request, 'foncier/infrastructures.html', context)


''',
    "vue 'infrastructures' retiree de views.py",
)

# 2. L'URL dans urls.py
remplacer(
    "foncier/urls.py",
    "    path('infrastructures/', views.infrastructures, name='infrastructures'),\n",
    "URL 'infrastructures/' retiree de urls.py",
)

# 3. Le lien dans le menu (base.html)
remplacer(
    "foncier/templates/foncier/base.html",
    '''        <li><a href="{% url 'infrastructures' %}">Infrastructures</a></li>
''',
    "lien navbar retire de base.html",
)

# 4. La tuile dans la page d'accueil (home.html)
remplacer(
    "foncier/templates/foncier/home.html",
    '''    <a href="{% url 'infrastructures' %}" class="km-bento-small">
      <div class="km-bs-icon"><i class="fa-solid fa-building"></i></div>
      <h4>Infrastructures</h4>
      <p>D&eacute;couvrez les &eacute;quipements publics et priv&eacute;s de la commune.</p>
      <span class="km-bs-link">En savoir plus <i class="fa-solid fa-arrow-right"></i></span>
    </a>

''',
    "tuile 'Infrastructures' retiree de home.html",
)

print("\n".join(resultats))