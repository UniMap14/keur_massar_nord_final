CHEMIN = "citoyens/templates/citoyens/base_citoyen.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''      <li><a href="{% url 'citoyen_plan_paiement_liste' %}" class="csidebar-link {% if active_section == 'plans_paiement' %}active{% endif %}">
        <i class="fa-solid fa-calendar-days"></i> Plans de paiement
      </a></li>'''

nouveau = ancre + '''
      <li><a href="{% url 'citoyen_morcellement_fusion_liste' %}" class="csidebar-link {% if active_section == 'morcellement_fusion' %}active{% endif %}">
        <i class="fa-solid fa-object-ungroup"></i> Morcellement / Fusion
      </a></li>'''

if "citoyen_morcellement_fusion_liste" in contenu and "Morcellement / Fusion" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Morcellement / Fusion' ajoute dans la sidebar.")
else:
    print("ERREUR : ancre introuvable.")