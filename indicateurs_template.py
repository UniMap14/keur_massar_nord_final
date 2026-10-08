# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_css = '''  /* ===== Intro texte au-dessus des fonctionnalites (page 3) ===== */'''

nouveau_css = '''  /* ===== Bande des indicateurs de transparence ===== */
  .km-transparence{
    background: linear-gradient(135deg, var(--km-brown-dark) 0%, #1a100b 100%);
    padding: 34px 60px;
  }
  .km-transparence-inner{
    max-width: 1100px; margin: 0 auto;
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
  }
  .km-transp-item{
    text-align: center; padding: 0 10px;
    border-right: 1px solid rgba(217,165,43,.2);
  }
  .km-transp-item:last-child{ border-right: none; }
  .km-transp-item i{ color: var(--km-gold); font-size: 20px; margin-bottom: 10px; display: block; }
  .km-transp-item strong{
    font-family: 'Playfair Display', serif; font-weight: 800;
    font-size: clamp(24px, 2.6vw, 32px); color: #fff; display: block; line-height: 1;
  }
  .km-transp-item span{
    display: block; margin-top: 8px; font-size: 11.5px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .5px; color: rgba(255,255,255,.65);
  }
  @media (max-width: 700px){
    .km-transparence{ padding: 26px 20px; }
    .km-transparence-inner{ grid-template-columns: 1fr; gap: 22px; }
    .km-transp-item{ border-right: none; border-bottom: 1px solid rgba(217,165,43,.2); padding-bottom: 18px; }
    .km-transp-item:last-child{ border-bottom: none; padding-bottom: 0; }
  }

  /* ===== Intro texte au-dessus des fonctionnalites (page 3) ===== */'''

if ".km-transparence{" in contenu:
    resultats.append("CSS : IGNORE (deja present)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS : OK")
else:
    resultats.append("CSS : ERREUR introuvable")

ancien_html = '''<section class="km-bento-section">'''

nouveau_html = '''<section class="km-transparence">
  <div class="km-transparence-inner">
    <div class="km-transp-item">
      <i class="fa-solid fa-map"></i>
      <strong>{{ total_parcelles }}</strong>
      <span>Parcelles cadastr&eacute;es</span>
    </div>
    <div class="km-transp-item">
      <i class="fa-solid fa-building"></i>
      <strong>{{ nb_infrastructures_total }}</strong>
      <span>Infrastructures recens&eacute;es</span>
    </div>
    <div class="km-transp-item">
      <i class="fa-solid fa-circle-check"></i>
      <strong>{{ pct_signalements_resolus }}%</strong>
      <span>Signalements r&eacute;solus</span>
    </div>
  </div>
</section>

<section class="km-bento-section">'''

if 'class="km-transparence"' in contenu:
    resultats.append("HTML : IGNORE (deja present)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML : OK (bande de transparence ajoutee)")
else:
    resultats.append("HTML : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))