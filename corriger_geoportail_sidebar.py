CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''      <li><a href="{% url 'geoportail_admin' %}" class="sidebar-link {% if active_section == 'geoportail' %}active{% endif %}">
        <i class="fa-solid fa-earth-africa nav-icon"></i> Géoportail
      </a></li>
    </ul>
    {% endif %}'''

nouveau = '''    </ul>
    {% endif %}

    {% if peut_technique or peut_fiscal %}
    <ul class="sidebar-nav">
      <li><a href="{% url 'geoportail_admin' %}" class="sidebar-link {% if active_section == 'geoportail' %}active{% endif %}">
        <i class="fa-solid fa-earth-africa nav-icon"></i> Géoportail
      </a></li>
    </ul>
    {% endif %}'''

if "peut_technique or peut_fiscal" in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien Geoportail deplace hors du bloc technique-only, visible aussi par l'agent fiscal.")
else:
    print("ERREUR : bloc exact introuvable.")