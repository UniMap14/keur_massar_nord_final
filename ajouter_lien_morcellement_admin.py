CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''      <li><a href="{% url 'dashboard_mutation_list' %}" class="sidebar-link {% if active_section == 'mutations' %}active{% endif %}">
        <i class="fa-solid fa-right-left nav-icon"></i> Mutations fiscales
      </a></li>'''

nouveau = ancre + '''
      <li><a href="{% url 'dashboard_morcellement_fusion_list' %}" class="sidebar-link {% if active_section == 'morcellement_fusion' %}active{% endif %}">
        <i class="fa-solid fa-object-ungroup nav-icon"></i> Morcellement / Fusion
      </a></li>'''

if "dashboard_morcellement_fusion_list" in contenu and "Morcellement / Fusion" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Morcellement / Fusion' ajoute dans la sidebar admin.")
else:
    print("ERREUR : ancre introuvable.")