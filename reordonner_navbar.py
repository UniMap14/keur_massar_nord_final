CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''      <ul id="navMenu">
        <li><a href="{% url 'home' %}">Accueil</a></li>
        <li><a href="{% url 'fiscalite' %}">Fiscalité</a></li>
        <li><a href="{% url 'galerie' %}">Galerie</a></li>
        <li><a href="{% url 'actualites' %}">Actualités</a></li>
        <li><a href="{% url 'contact' %}">Contact</a></li>
        <li><a href="{% url 'dashboard_home' %}">Gestion</a></li>
      </ul>'''

nouveau = '''      <ul id="navMenu">
        <li><a href="{% url 'home' %}">Accueil</a></li>
        <li><a href="{% url 'actualites' %}">Actualités</a></li>
        <li><a href="{% url 'fiscalite' %}">Fiscalité</a></li>
        <li><a href="{% url 'contact' %}">Contact</a></li>
        <li><a href="{% url 'galerie' %}">Galerie</a></li>
        <li><a href="{% url 'dashboard_home' %}">Gestion</a></li>
      </ul>'''

if contenu.count(nouveau) >= 1 and ancien not in contenu:
    print("DEJA FAIT : ordre deja correct.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : menu reordonne.")
else:
    print("ERREUR : bloc exact introuvable (verifie que le menu correspond au dernier etat connu).")