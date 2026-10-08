# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''<section class="km-page2" id="page-chiffres">
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
</section>'''

nouveau = '''<section class="km-page2" id="page-chiffres">

  <div class="km-page2-weather-badge">
    <div class="km-weather-box" id="kmWeatherBox">
      <div class="km-weather-loading"><i class="fa-solid fa-spinner fa-spin"></i> M&eacute;t&eacute;o&hellip;</div>
    </div>
  </div>

  <div class="km-page2-stats-bar">
    <div class="km-page2-stat">
      <i class="fa-solid fa-people-group"></i>
      <strong>{{ population|default:"224 765" }}</strong>
      <span>Habitants</span>
    </div>
    <div class="km-page2-stat">
      <i class="fa-solid fa-city"></i>
      <strong>{{ nb_quartiers|default:"104" }}</strong>
      <span>Quartiers</span>
    </div>
    <div class="km-page2-stat">
      <i class="fa-regular fa-calendar"></i>
      <strong>{{ annee_creation|default:"2021" }}</strong>
      <span>Fondation</span>
    </div>
    <div class="km-page2-stat">
      <i class="fa-solid fa-vector-square"></i>
      <strong>{{ superficie|default:"13,18" }}</strong>
      <span>km&sup2; superficie</span>
    </div>
  </div>

  <div class="km-page2-maire">
    <div class="km-page2-maire-text">
      <span class="km-page2-eyebrow-line">Le mot du maire</span>
      <h2>Une commune en pleine<br><em>modernisation</em></h2>
      <p class="km-page2-quote"><i class="fa-solid fa-quote-left"></i> Soyons ensemble les acteurs des changements auxquels nous aspirons.</p>
      <p class="km-page2-bio">Maire de la Commune de Keur Massar Nord (mandature 2022&ndash;2027), ing&eacute;nieur g&eacute;om&egrave;tre-topographe et doctorant en g&eacute;omatique &agrave; l'Universit&eacute; Laval. Ce portail est notre engagement pour une gestion fonci&egrave;re et fiscale plus transparente et plus proche de vous.</p>
      <div class="km-page2-maire-actions">
        <a href="{% url 'geoportail' %}" class="btn-km-primary">
          <i class="fa-solid fa-map-location-dot"></i> Ouvrir le g&eacute;oportail de la commune
        </a>
      </div>
    </div>

    <div class="km-page2-photo-wrap">
      <img src="{% static 'foncier/img/maire-adama-sarr.jpg' %}" alt="Adama Sarr, Maire de Keur Massar Nord" class="km-page2-photo" loading="lazy">
    </div>
  </div>

</section>'''

if "km-page2-stats-bar" in contenu and "<div class=\"km-page2-stats-bar\">" in contenu:
    print("IGNORE : HTML page2 v2 deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : HTML page2 remplace par la version v2.")
else:
    print("ERREUR : bloc HTML page2 (v1) introuvable tel quel.")