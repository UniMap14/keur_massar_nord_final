CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''      <li><a href="{% url 'dashboard_plan_paiement_list' %}" class="sidebar-link {% if active_section == 'plans_paiement' %}active{% endif %}">
        <i class="fa-solid fa-calendar-days nav-icon"></i> Plans de paiement
      </a></li>'''

nouveau = ancre + '''
      <li><a href="{% url 'dashboard_mutation_list' %}" class="sidebar-link {% if active_section == 'mutations' %}active{% endif %}">
        <i class="fa-solid fa-right-left nav-icon"></i> Mutations fiscales
      </a></li>'''

if "dashboard_mutation_list" in contenu and "Mutations fiscales" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Mutations fiscales' ajoute dans la sidebar admin.")
else:
    print("ERREUR : ancre introuvable.")