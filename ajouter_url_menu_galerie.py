CHEMIN_URLS = "foncier/dashboard_urls.py"
CHEMIN_BASE = "foncier/templates/dashboard/base.html"

resultats = []

with open(CHEMIN_URLS, encoding="utf-8") as f:
    urls = f.read()

ancien_urls = '''    # --- Espace Jeunes (projets soumis par les jeunes de la commune) ---
    path("jeunesse/", views.dashboard_jeunesse_list, name="dashboard_jeunesse_list"),
    path("jeunesse/<int:pk>/", views.dashboard_jeunesse_detail, name="dashboard_jeunesse_detail"),
]'''

nouveau_urls = '''    # --- Espace Jeunes (projets soumis par les jeunes de la commune) ---
    path("jeunesse/", views.dashboard_jeunesse_list, name="dashboard_jeunesse_list"),
    path("jeunesse/<int:pk>/", views.dashboard_jeunesse_detail, name="dashboard_jeunesse_detail"),

    # --- Galerie photo (page publique "La commune en images") ---
    path("galerie/", views.dashboard_galerie_list, name="dashboard_galerie_list"),
    path("galerie/nouvelle/", views.dashboard_galerie_create, name="dashboard_galerie_create"),
    path("galerie/<int:pk>/modifier/", views.dashboard_galerie_update, name="dashboard_galerie_update"),
    path("galerie/<int:pk>/supprimer/", views.dashboard_galerie_delete, name="dashboard_galerie_delete"),
]'''

if "dashboard_galerie_list" in urls:
    resultats.append("urls.py : IGNORE (deja present)")
elif ancien_urls in urls:
    urls = urls.replace(ancien_urls, nouveau_urls, 1)
    with open(CHEMIN_URLS, "w", encoding="utf-8", newline="") as f:
        f.write(urls)
    resultats.append("urls.py : OK (4 routes ajoutees)")
else:
    resultats.append("urls.py : ERREUR ancre introuvable")

with open(CHEMIN_BASE, encoding="utf-8") as f:
    base = f.read()

ancien_lien = '''      <li><a href="{% url 'dashboard_actualite_list' %}" class="sidebar-link {% if active_section == 'actualites' %}active{% endif %}">
        <i class="fa-solid fa-newspaper nav-icon"></i> Actualités
      </a></li>
    </ul>
    {% endif %}'''

nouveau_lien = '''      <li><a href="{% url 'dashboard_actualite_list' %}" class="sidebar-link {% if active_section == 'actualites' %}active{% endif %}">
        <i class="fa-solid fa-newspaper nav-icon"></i> Actualités
      </a></li>
      <li><a href="{% url 'dashboard_galerie_list' %}" class="sidebar-link {% if active_section == 'galerie' %}active{% endif %}">
        <i class="fa-solid fa-images nav-icon"></i> Galerie photo
      </a></li>
    </ul>
    {% endif %}'''

if "dashboard_galerie_list" in base:
    resultats.append("base.html : IGNORE (deja present)")
elif ancien_lien in base:
    base = base.replace(ancien_lien, nouveau_lien, 1)
    with open(CHEMIN_BASE, "w", encoding="utf-8", newline="") as f:
        f.write(base)
    resultats.append("base.html : OK (lien de menu ajoute)")
else:
    resultats.append("base.html : ERREUR ancre introuvable")

print("\n".join(resultats))