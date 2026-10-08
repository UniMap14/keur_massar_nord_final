CHEMIN_URLS = "foncier/dashboard_urls.py"
CHEMIN_BASE = "foncier/templates/dashboard/base.html"

resultats = []

# --- 1. URLs ---
with open(CHEMIN_URLS, encoding="utf-8") as f:
    urls = f.read()

ancien_urls = '''    # --- Journal d'audit (réservé aux superviseurs) ---
    path("journal-audit/", views.dashboard_journal_audit_list, name="dashboard_journal_audit_list"),
]'''

nouveau_urls = '''    # --- Journal d'audit (réservé aux superviseurs) ---
    path("journal-audit/", views.dashboard_journal_audit_list, name="dashboard_journal_audit_list"),

    # --- Espace Jeunes (projets soumis par les jeunes de la commune) ---
    path("jeunesse/", views.dashboard_jeunesse_list, name="dashboard_jeunesse_list"),
    path("jeunesse/<int:pk>/", views.dashboard_jeunesse_detail, name="dashboard_jeunesse_detail"),
]'''

if "dashboard_jeunesse_list" in urls:
    resultats.append("urls.py : IGNORE (deja present)")
elif ancien_urls in urls:
    urls = urls.replace(ancien_urls, nouveau_urls, 1)
    with open(CHEMIN_URLS, "w", encoding="utf-8", newline="") as f:
        f.write(urls)
    resultats.append("urls.py : OK (2 routes ajoutees)")
else:
    resultats.append("urls.py : ERREUR ancre introuvable")

# --- 2. Lien de menu (section Citoyens, a cote de Signalements) ---
with open(CHEMIN_BASE, encoding="utf-8") as f:
    base = f.read()

ancien_lien = '''      {% if peut_technique %}
      <li><a href="{% url 'dashboard_signalement_list' %}" class="sidebar-link {% if active_section == 'signalements' %}active{% endif %}">
        <i class="fa-solid fa-triangle-exclamation nav-icon"></i> Signalements citoyens
        {% if nb_signalements_en_cours %}<span class="count count-alert">{{ nb_signalements_en_cours }}</span>{% endif %}
      </a></li>
      {% endif %}
    </ul>'''

nouveau_lien = '''      {% if peut_technique %}
      <li><a href="{% url 'dashboard_signalement_list' %}" class="sidebar-link {% if active_section == 'signalements' %}active{% endif %}">
        <i class="fa-solid fa-triangle-exclamation nav-icon"></i> Signalements citoyens
        {% if nb_signalements_en_cours %}<span class="count count-alert">{{ nb_signalements_en_cours }}</span>{% endif %}
      </a></li>
      {% endif %}
      <li><a href="{% url 'dashboard_jeunesse_list' %}" class="sidebar-link {% if active_section == 'jeunesse' %}active{% endif %}">
        <i class="fa-solid fa-seedling nav-icon"></i> Espace Jeunes
      </a></li>
    </ul>'''

if "dashboard_jeunesse_list" in base:
    resultats.append("base.html : IGNORE (deja present)")
elif ancien_lien in base:
    base = base.replace(ancien_lien, nouveau_lien, 1)
    with open(CHEMIN_BASE, "w", encoding="utf-8", newline="") as f:
        f.write(base)
    resultats.append("base.html : OK (lien de menu ajoute)")
else:
    resultats.append("base.html : ERREUR ancre introuvable")

print("\n".join(resultats))