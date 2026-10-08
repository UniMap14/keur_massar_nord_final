# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_html = '''<section class="km-hero" id="hero">
  <video class="km-hero-video" autoplay muted loop playsinline
       poster="{% static 'foncier/img/gallery/fond-keurmassar.png' %}">
  <source src="{% static 'foncier/video/fond-keurmassar.mp4' %}" type="video/mp4">
</video>
  <div class="km-hero-inner">
    <div class="km-hero-left">
      <div class="km-hero-welcome">
        <p class="km-hero-welcome-text">Bienvenue &agrave; Keur Massar Nord</p>
        <a href="#apres-hero" class="btn-km-primary" id="btnDecouvrir">
          <i class="fa-solid fa-building-columns"></i> D&eacute;couvrir la commune
        </a>
      </div>
    </div>

    <div class="km-hero-right">
      <div class="km-stats-panel">
        <h3>Keur Massar en chiffres</h3>
        <div class="km-stats-grid">
          <div class="km-stat-item">
            <i class="fa-solid fa-people-group"></i>
            <strong>{{ population|default:"224 765" }}</strong>
            <span>Population</span>
          </div>
          <div class="km-stat-item">
            <i class="fa-solid fa-vector-square"></i>
            <strong>{{ superficie|default:"13,18" }} km&sup2;</strong>
            <span>Superficie</span>
          </div>
          <div class="km-stat-item">
            <i class="fa-solid fa-city"></i>
            <strong>{{ nb_quartiers|default:"104" }}</strong>
            <span>Quartiers</span>
          </div>
          <div class="km-stat-item">
            <i class="fa-regular fa-calendar"></i>
            <strong>{{ annee_creation|default:"2021" }}</strong>
            <span>Ann&eacute;e de cr&eacute;ation</span>
          </div>
        </div>
      </div>

      <div class="km-weather-box" id="kmWeatherBox">
        <div class="km-weather-loading"><i class="fa-solid fa-spinner fa-spin"></i> M&eacute;t&eacute;o en cours de chargement&hellip;</div>
      </div>

      <div class="km-mayor-card">
        <img src="{% static 'foncier/img/maire-adama-sarr.jpg' %}" alt="Adama Sarr, Maire de Keur Massar Nord" class="km-mayor-photo" loading="lazy">
        <div class="km-mayor-text">
          <h5>Mot du Maire</h5>
          <p>Maire de la Commune de Keur Massar Nord (mandature 2022&ndash;2027), ing&eacute;nieur g&eacute;om&egrave;tre-topographe et doctorant en g&eacute;omatique &agrave; l'Universit&eacute; Laval &mdash; &laquo; Soyons ensemble les acteurs des changements auxquels nous aspirons. &raquo;</p>
        </div>
      </div>
    </div>
  </div>


</section>

<div id="apres-hero"></div>

<section class="km-bento-section">'''

nouveau_html = '''<section class="km-hero" id="hero">
  <video class="km-hero-video" autoplay muted loop playsinline
       poster="{% static 'foncier/img/gallery/fond-keurmassar.png' %}">
  <source src="{% static 'foncier/video/fond-keurmassar.mp4' %}" type="video/mp4">
</video>
  <div class="km-hero-inner">
    <div class="km-hero-left">
      <div class="km-hero-welcome">
        <p class="km-hero-welcome-text">Bienvenue &agrave; Keur Massar Nord</p>
        <a href="#page-chiffres" class="btn-km-primary" id="btnDecouvrir">
          <i class="fa-solid fa-building-columns"></i> D&eacute;couvrir la commune
        </a>
      </div>
    </div>
  </div>
</section>

<section class="km-page2" id="page-chiffres">
  <div class="km-page2-inner">
    <div class="km-page2-left">
      <span class="km-page2-eyebrow"><i class="fa-solid fa-chart-simple"></i> La commune en un coup d'&oelig;il</span>
      <div class="km-stats-panel km-stats-panel-big">
        <h3>Keur Massar en chiffres</h3>
        <div class="km-stats-grid">
          <div class="km-stat-item">
            <i class="fa-solid fa-people-group"></i>
            <strong>{{ population|default:"224 765" }}</strong>
            <span>Population</span>
          </div>
          <div class="km-stat-item">
            <i class="fa-solid fa-vector-square"></i>
            <strong>{{ superficie|default:"13,18" }} km&sup2;</strong>
            <span>Superficie</span>
          </div>
          <div class="km-stat-item">
            <i class="fa-solid fa-city"></i>
            <strong>{{ nb_quartiers|default:"104" }}</strong>
            <span>Quartiers</span>
          </div>
          <div class="km-stat-item">
            <i class="fa-regular fa-calendar"></i>
            <strong>{{ annee_creation|default:"2021" }}</strong>
            <span>Ann&eacute;e de cr&eacute;ation</span>
          </div>
        </div>
      </div>
      <div class="km-weather-box" id="kmWeatherBox">
        <div class="km-weather-loading"><i class="fa-solid fa-spinner fa-spin"></i> M&eacute;t&eacute;o en cours de chargement&hellip;</div>
      </div>
    </div>

    <div class="km-page2-right">
      <div class="km-mayor-card km-mayor-card-big">
        <img src="{% static 'foncier/img/maire-adama-sarr.jpg' %}" alt="Adama Sarr, Maire de Keur Massar Nord" class="km-mayor-photo" loading="lazy">
        <div class="km-mayor-text">
          <h5>Mot du Maire</h5>
          <p>Maire de la Commune de Keur Massar Nord (mandature 2022&ndash;2027), ing&eacute;nieur g&eacute;om&egrave;tre-topographe et doctorant en g&eacute;omatique &agrave; l'Universit&eacute; Laval &mdash; &laquo; Soyons ensemble les acteurs des changements auxquels nous aspirons. &raquo;</p>
        </div>
      </div>
      <a href="{% url 'geoportail' %}" class="btn-km-primary km-page2-cta">
        <i class="fa-solid fa-map-location-dot"></i> Ouvrir le g&eacute;oportail de la commune
      </a>
    </div>
  </div>
</section>

<div id="apres-hero"></div>

<section class="km-bento-section">

  <div class="km-bento-intro">
    <span class="section-label">Fonctionnalit&eacute;s</span>
    <h2>Tout ce dont vous avez besoin, en un seul endroit</h2>
    <p>G&eacute;oportail, fiscalit&eacute;, d&eacute;marches en ligne, actualit&eacute;s&hellip; d&eacute;couvrez les outils mis &agrave; votre disposition par la commune de Keur Massar Nord.</p>
  </div>'''

if 'id="page-chiffres"' in contenu:
    resultats.append("HTML : IGNORE (deja present)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML : OK (page 1 simplifiee, page 2 creee, intro page 3 ajoutee)")
else:
    resultats.append("HTML : ERREUR bloc introuvable tel quel")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))