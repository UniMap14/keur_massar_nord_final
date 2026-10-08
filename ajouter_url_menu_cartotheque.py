CHEMIN_URLS = "foncier/dashboard_urls.py"
CHEMIN_BASE = "foncier/templates/dashboard/base.html"

resultats = []

with open(CHEMIN_URLS, encoding="utf-8") as f:
    urls = f.read()

ancien_urls = '''    # --- Galerie photo (page publique "La commune en images") ---
    path("galerie/", views.dashboard_galerie_list, name="dashboard_galerie_list"),
    path("galerie/nouvelle/", views.dashboard_galerie_create, name="dashboard_galerie_create"),
    path("galerie/<int:pk>/modifier/", views.dashboard_galerie_update, name="dashboard_galerie_update"),
    path("galerie/<int:pk>/supprimer/", views.dashboard_galerie_delete, name="dashboard_galerie_delete"),
]'''

nouveau_urls = '''    # --- Galerie photo (page publique "La commune en images") ---
    path("galerie/", views.dashboard_galerie_list, name="dashboard_galerie_list"),
    path("galerie/nouvelle/", views.dashboard_galerie_create, name="dashboard_galerie_create"),
    path("galerie/<int:pk>/modifier/", views.dashboard_galerie_update, name="dashboard_galerie_update"),
    path("galerie/<int:pk>/supprimer/", views.dashboard_galerie_delete, name="dashboard_galerie_delete"),

    # --- Cartotheque (page publique "Cartotheque") ---
    path("cartotheque/", views.dashboard_cartotheque_list, name="dashboard_cartotheque_list"),
    path("cartotheque/nouvelle/", views.dashboard_cartotheque_create, name="dashboard_cartotheque_create"),
    path("cartotheque/<int:pk>/modifier/", views.dashboard_cartotheque_update, name="dashboard_cartotheque_update"),
    path("cartotheque/<int:pk>/supprimer/", views.dashboard_cartotheque_delete, name="dashboard_cartotheque_delete"),
]'''

if "dashboard_cartotheque_list" in urls:
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

ancien_lien = '''      <li><a href="{% url 'dashboard_galerie_list' %}" class="sidebar-link {% if active_section == 'galerie' %}active{% endif %}">
        <i class="fa-solid fa-images nav-icon"></i> Galerie photo
      </a></li>
    </ul>
    {% endif %}'''

nouveau_lien = '''      <li><a href="{% url 'dashboard_galerie_list' %}" class="sidebar-link {% if active_section == 'galerie' %}active{% endif %}">
        <i class="fa-solid fa-images nav-icon"></i> Galerie photo
      </a></li>
      <li><a href="{% url 'dashboard_cartotheque_list' %}" class="sidebar-link {% if active_section == 'cartotheque' %}active{% endif %}">
        <i class="fa-solid fa-map-location-dot nav-icon"></i> Cartothèque
      </a></li>
    </ul>
    {% endif %}'''

if "dashboard_cartotheque_list" in base:
    resultats.append("base.html : IGNORE (deja present)")
elif ancien_lien in base:
    base = base.replace(ancien_lien, nouveau_lien, 1)
    with open(CHEMIN_BASE, "w", encoding="utf-8", newline="") as f:
        f.write(base)
    resultats.append("base.html : OK (lien de menu ajoute)")
else:
    resultats.append("base.html : ERREUR ancre introuvable")

print("\n".join(resultats))