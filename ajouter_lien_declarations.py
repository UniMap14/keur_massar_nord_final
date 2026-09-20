CHEMIN = "citoyens/templates/citoyens/base_citoyen.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''      <li><a href="{% url 'citoyen_demandes' %}" class="csidebar-link {% if active_section == 'demandes' %}active{% endif %}">
        <i class="fa-solid fa-folder-open"></i> Mes démarches
      </a></li>'''

nouveau = ancre + '''
      <li><a href="{% url 'citoyen_declarations' %}" class="csidebar-link {% if active_section == 'declarations' %}active{% endif %}">
        <i class="fa-solid fa-file-signature"></i> Mes déclarations
      </a></li>'''

if "citoyen_declarations" in contenu and "Mes déclarations" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Mes déclarations' ajoute dans la sidebar.")
else:
    print("ERREUR : ancre introuvable.")