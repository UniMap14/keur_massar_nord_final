# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_html = '''    <nav aria-label="Navigation principale">
      <ul id="navMenu">
        <li><a href="{% url 'home' %}">Accueil</a></li>
        <li><a href="{% url 'actualites' %}">Actualités</a></li>
        <li><a href="{% url 'fiscalite' %}">Fiscalité</a></li>
        <li><a href="{% url 'contact' %}">Contact</a></li>
        <li><a href="{% url 'galerie' %}">Galerie</a></li>
        <li><a href="{% url 'cartotheque' %}">Cartothèque</a></li>
        <li><a href="{% url 'dashboard_home' %}">Gestion</a></li>
      </ul>
    </nav>
    <div class="km-header-right">
      <img src="{% static 'foncier/images/logo-uidt.png' %}" alt="Logo Université Iba Der Thiam de Thiès" class="logo-uidt-img">'''

nouveau_html = '''    <nav aria-label="Navigation principale">
      <ul id="navMenu">
        <li><a href="{% url 'home' %}"><i class="fa-solid fa-house"></i> Accueil</a></li>
        <li><a href="{% url 'actualites' %}"><i class="fa-solid fa-newspaper"></i> Actualités</a></li>
        <li><a href="{% url 'foncier_info' %}"><i class="fa-solid fa-landmark-dome"></i> Foncier</a></li>
        <li><a href="{% url 'fiscalite' %}"><i class="fa-solid fa-scale-balanced"></i> Fiscalité</a></li>
        <li><a href="{% url 'cartotheque' %}"><i class="fa-solid fa-map-location-dot"></i> Cartothèque</a></li>
        <li><a href="{% url 'galerie' %}"><i class="fa-solid fa-images"></i> Galerie</a></li>
        <li><a href="{% url 'contact' %}"><i class="fa-solid fa-envelope"></i> Contact</a></li>
      </ul>
    </nav>
    <div class="km-header-right">
      <a href="{% url 'dashboard_home' %}" class="nav-gestion-link">
        <i class="fa-solid fa-right-to-bracket"></i> Gestion
      </a>
      <img src="{% static 'foncier/images/logo-uidt.png' %}" alt="Logo Université Iba Der Thiam de Thiès" class="logo-uidt-img">'''

if 'class="nav-gestion-link"' in contenu:
    resultats.append("HTML navbar : IGNORE (deja present)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML navbar : OK (reorganise, icones ajoutees, Gestion deplace)")
else:
    resultats.append("HTML navbar : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))