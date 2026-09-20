CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''      <li><a href="{% url 'dashboard_contribuable_list' %}" class="sidebar-link {% if active_section == 'contribuables' %}active{% endif %}">
        <i class="fa-solid fa-id-card nav-icon"></i> Contribuables
      </a></li>'''

nouveau = '''      <li><a href="{% url 'dashboard_declaration_list' %}" class="sidebar-link {% if active_section == 'declarations' %}active{% endif %}">
        <i class="fa-solid fa-file-signature nav-icon"></i> Déclarations fiscales
      </a></li>
      <li><a href="{% url 'dashboard_contribuable_list' %}" class="sidebar-link {% if active_section == 'contribuables' %}active{% endif %}">
        <i class="fa-solid fa-id-card nav-icon"></i> Contribuables
      </a></li>'''

if "dashboard_declaration_list" in contenu and "Déclarations fiscales" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Declarations fiscales' ajoute dans la sidebar admin.")
else:
    print("ERREUR : ancre introuvable.")