CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''      <li><a href="{% url 'dashboard_recours_list' %}" class="sidebar-link {% if active_section == 'recours' %}active{% endif %}">
        <i class="fa-solid fa-scale-balanced nav-icon"></i> Recours fiscaux
      </a></li>'''

nouveau = ancre + '''
      <li><a href="{% url 'dashboard_immatriculation_list' %}" class="sidebar-link {% if active_section == 'immatriculations' %}active{% endif %}">
        <i class="fa-solid fa-user-plus nav-icon"></i> Premières immatriculations
      </a></li>'''

if "dashboard_immatriculation_list" in contenu and "immatriculations" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Premieres immatriculations' ajoute dans la sidebar admin.")
else:
    print("ERREUR : ancre introuvable.")