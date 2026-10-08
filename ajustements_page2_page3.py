# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. Image plus petite + contenu remonte sur la Page 2
# ============================================================
ancien_css = '''  .km-page2{
    position:relative; min-height:100vh; display:flex; flex-direction:column; justify-content:center;
    background: var(--km-cream);
    padding:80px 60px 60px;
  }'''

nouveau_css = '''  .km-page2{
    position:relative; min-height:100vh; display:flex; flex-direction:column; justify-content:center;
    background: var(--km-cream);
    padding:50px 60px 40px;
  }'''

if "padding:50px 60px 40px;" in contenu:
    resultats.append("CSS padding page2 : IGNORE (deja present)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS padding page2 : OK (contenu remonte)")
else:
    resultats.append("CSS padding page2 : ERREUR introuvable")

ancien_css2 = '''  .km-page2-stats-bar{
    display:grid; grid-template-columns:repeat(4,1fr);
    max-width:1180px; margin:0 auto 76px; position:relative;
  }'''

nouveau_css2 = '''  .km-page2-stats-bar{
    display:grid; grid-template-columns:repeat(4,1fr);
    max-width:1180px; margin:0 auto 50px; position:relative;
  }'''

if "margin:0 auto 50px; position:relative;" in contenu:
    resultats.append("CSS marge stats-bar : IGNORE (deja present)")
elif ancien_css2 in contenu:
    contenu = contenu.replace(ancien_css2, nouveau_css2, 1)
    resultats.append("CSS marge stats-bar : OK (reduite)")
else:
    resultats.append("CSS marge stats-bar : ERREUR introuvable")

ancien_css3 = '''  .km-page2-photo{
    position:relative; z-index:1; width:100%; aspect-ratio:4/4.6; object-fit:cover;
    border-radius:var(--km-radius); box-shadow:var(--km-shadow-lg); display:block;
  }'''

nouveau_css3 = '''  .km-page2-photo{
    position:relative; z-index:1; width:100%; max-height:380px; aspect-ratio:4/3.8; object-fit:cover;
    border-radius:var(--km-radius); box-shadow:var(--km-shadow-lg); display:block;
  }'''

if "max-height:380px; aspect-ratio:4/3.8;" in contenu:
    resultats.append("CSS photo page2 : IGNORE (deja present)")
elif ancien_css3 in contenu:
    contenu = contenu.replace(ancien_css3, nouveau_css3, 1)
    resultats.append("CSS photo page2 : OK (reduite)")
else:
    resultats.append("CSS photo page2 : ERREUR introuvable")

# ============================================================
# 2. Suppression de l'intro texte (page 3) ET de la carte
#    "Fonctionnalite phare / Explorez le Geoportail" en double
# ============================================================
ancien_html = '''<section class="km-bento-section">

  <div class="km-bento-intro">
    <span class="section-label">Fonctionnalit&eacute;s</span>
    <h2>Tout ce dont vous avez besoin, en un seul endroit</h2>
    <p>G&eacute;oportail, fiscalit&eacute;, d&eacute;marches en ligne, actualit&eacute;s&hellip; d&eacute;couvrez les outils mis &agrave; votre disposition par la commune de Keur Massar Nord.</p>
  </div>

  <a href="{% url 'geoportail' %}" class="km-bento-featured">
    <div class="km-bf-left">
      <div class="km-bf-icon"><i class="fa-solid fa-map-location-dot"></i></div>
      <div class="km-bf-text">
        <span class="km-bf-badge"><i class="fa-solid fa-star"></i> Fonctionnalit&eacute; phare</span>
        <h3>Explorez le <span class="km-bf-highlight">G&eacute;oportail</span></h3>
        <p>Visualisez en temps r&eacute;el toutes les parcelles cadastrales, leur statut fiscal et les infrastructures environnantes sur une carte interactive.</p>
      </div>
    </div>
    <span class="km-bf-cta">Ouvrir la carte interactive <i class="fa-solid fa-arrow-right"></i></span>
  </a>

  <div class="km-bento-grid-small">'''

nouveau_html = '''<section class="km-bento-section">

  <div class="km-bento-grid-small">'''

if ('<div class="km-bento-intro">' not in contenu) and ('class="km-bento-featured"' not in contenu):
    resultats.append("HTML page3 : IGNORE (deja supprime)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML page3 : OK (intro + carte Geoportail en double supprimees)")
else:
    resultats.append("HTML page3 : ERREUR bloc introuvable tel quel")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))