CHEMIN = "citoyens/templates/citoyens/base_citoyen.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''      <li><a href="{% url 'citoyen_calendrier_fiscal' %}" class="csidebar-link {% if active_section == 'calendrier' %}active{% endif %}">
        <i class="fa-solid fa-calendar-days"></i> Calendrier fiscal
      </a></li>'''

nouveau = ancre + '''
      <li><a href="{% url 'citoyen_exoneration_liste' %}" class="csidebar-link {% if active_section == 'exonerations' %}active{% endif %}">
        <i class="fa-solid fa-house-circle-check"></i> Mes exonérations
      </a></li>'''

if "citoyen_exoneration_liste" in contenu and "Mes exonérations" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Mes exonerations' ajoute dans la sidebar.")
else:
    print("ERREUR : ancre introuvable.")