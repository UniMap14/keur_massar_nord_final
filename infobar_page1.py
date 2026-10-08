# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. CSS de la bande d'infos pratiques
# ============================================================
ancien_css = '''  /* --- Ticker d'actualites (en haut de page) --- */'''

nouveau_css = '''  /* ===== Bande d'infos pratiques (bas de la Page 1) ===== */
  .km-hero-infobar{
    position:absolute; bottom:0; left:0; right:0; z-index:3;
    background:rgba(20,14,10,.6); backdrop-filter:blur(6px);
    border-top:1px solid rgba(217,165,43,.25);
  }
  .km-hero-infobar-inner{
    max-width:1320px; margin:0 auto; padding:12px 60px;
    display:flex; align-items:center; gap:26px; flex-wrap:wrap; justify-content:center;
  }
  .km-ib-item{
    display:inline-flex; align-items:center; gap:7px;
    font-size:12.5px; color:rgba(255,255,255,.85); text-decoration:none; white-space:nowrap;
    transition:color .2s ease; background:none; border:none; cursor:pointer; font-family:inherit;
  }
  .km-ib-item i{ color:var(--km-gold); font-size:11px; }
  .km-ib-item:hover{ color:var(--km-gold-light); }
  .km-ib-highlight{ font-weight:700; color:var(--km-gold-light); }
  .km-ib-social{ display:flex; align-items:center; gap:10px; margin-left:4px; }
  .km-ib-social a{
    width:26px; height:26px; border-radius:50%; background:rgba(255,255,255,.1);
    display:flex; align-items:center; justify-content:center; color:#fff; font-size:11px;
    transition:background .2s ease;
  }
  .km-ib-social a:hover{ background:var(--km-gold); color:var(--km-brown-dark); }

  @media (max-width: 991px){
    .km-hero-infobar-inner{ padding:10px 20px; gap:14px; }
    .km-ib-item{ font-size:11px; }
  }
  @media (max-width: 700px){
    .km-hero-infobar{ position:static; background:var(--km-brown-dark); }
  }

  /* --- Ticker d'actualites (en haut de page) --- */'''

if ".km-hero-infobar{" in contenu:
    resultats.append("CSS infobar : IGNORE (deja present)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS infobar : OK")
else:
    resultats.append("CSS infobar : ERREUR introuvable")

# ============================================================
# 2. HTML : insertion de la bande juste avant la fermeture de km-hero
# ============================================================
ancien_html = '''    </div>
  </div>
</section>

<section class="km-page2" id="page-chiffres">'''

nouveau_html = '''    </div>
  </div>

  <div class="km-hero-infobar">
    <div class="km-hero-infobar-inner">
      <a href="tel:+221338892002" class="km-ib-item"><i class="fa-solid fa-phone"></i> +221 33 840 61 84</a>
      <a href="mailto:info@keurmassarnord.com" class="km-ib-item"><i class="fa-solid fa-envelope"></i> info@keurmassarnord.com</a>
      <span class="km-ib-item"><i class="fa-solid fa-location-dot"></i> Keur Massar Nord, Dakar</span>
      <span class="km-ib-item"><i class="fa-solid fa-clock"></i> Lun&ndash;Ven, 8h&ndash;17h</span>
      <a href="#page-chiffres" class="km-ib-item km-ib-highlight" id="btnMotDuMaireBas"><i class="fa-solid fa-user-tie"></i> Mot du Maire</a>
      <a href="{% url 'foncier_info' %}" class="km-ib-item"><i class="fa-solid fa-landmark-dome"></i> Foncier</a>
      <a href="{% url 'fiscalite' %}" class="km-ib-item"><i class="fa-solid fa-scale-balanced"></i> Fiscalit&eacute;</a>
      <div class="km-ib-social">
        <a href="#" aria-label="Facebook" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-facebook-f"></i></a>
        <a href="#" aria-label="X (Twitter)" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-x-twitter"></i></a>
        <a href="#" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-linkedin-in"></i></a>
      </div>
    </div>
  </div>
</section>

<section class="km-page2" id="page-chiffres">'''

if 'km-hero-infobar"' in contenu and '<div class="km-hero-infobar">' in contenu:
    resultats.append("HTML infobar : IGNORE (deja present)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML infobar : OK (bande ajoutee en bas de la Page 1)")
else:
    resultats.append("HTML infobar : ERREUR bloc introuvable tel quel")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))