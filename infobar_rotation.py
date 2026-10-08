# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. CSS : remplace le defilement continu par une rotation
#    (un seul element visible a la fois, change toutes les 3s)
# ============================================================
ancien_css = '''  .km-hero-infobar{
    position:absolute; bottom:52px; left:0; right:0; z-index:3;
    background:rgba(20,14,10,.6); backdrop-filter:blur(6px);
    border-top:1px solid rgba(217,165,43,.25);
    overflow:hidden;
  }
  .km-hero-infobar-inner{
    display:flex; align-items:center; gap:30px;
    padding:12px 0; white-space:nowrap; width:max-content;
    animation: kmInfobarScroll 26s linear infinite;
  }
  .km-hero-infobar:hover .km-hero-infobar-inner{ animation-play-state:paused; }
  @keyframes kmInfobarScroll{
    from{ transform:translateX(0); }
    to{ transform:translateX(-50%); }
  }'''

nouveau_css = '''  .km-hero-infobar{
    position:absolute; bottom:52px; left:0; right:0; z-index:3;
    background:rgba(20,14,10,.6); backdrop-filter:blur(6px);
    border-top:1px solid rgba(217,165,43,.25);
  }
  .km-hero-infobar-inner{
    max-width:1320px; margin:0 auto; padding:14px 60px;
    display:flex; align-items:center; justify-content:center; gap:24px;
  }
  .km-ib-rotator{ position:relative; height:18px; flex:1; max-width:420px; }
  .km-ib-slide{
    position:absolute; inset:0; display:flex; align-items:center; justify-content:center; gap:7px;
    opacity:0; transform:translateY(6px); transition:opacity .5s ease, transform .5s ease;
    pointer-events:none;
  }
  .km-ib-slide.is-active{ opacity:1; transform:translateY(0); pointer-events:auto; }'''

if ".km-ib-rotator{" in contenu:
    resultats.append("CSS rotation : IGNORE (deja present)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS rotation : OK (remplace le defilement continu)")
else:
    resultats.append("CSS rotation : ERREUR introuvable")

# ============================================================
# 2. HTML : retire la duplication, remet un seul jeu d'items
#    en mode "diapositives" empilees
# ============================================================
ancien_html = '''  <div class="km-hero-infobar">
    <div class="km-hero-infobar-inner">
      <a href="tel:+221338892002" class="km-ib-item"><i class="fa-solid fa-phone"></i> +221 33 840 61 84</a>
      <a href="mailto:info@keurmassarnord.com" class="km-ib-item"><i class="fa-solid fa-envelope"></i> info@keurmassarnord.com</a>
      <span class="km-ib-item"><i class="fa-solid fa-location-dot"></i> Keur Massar Nord, Dakar</span>
      <span class="km-ib-item"><i class="fa-solid fa-clock"></i> Lun&ndash;Ven, 8h&ndash;17h</span>
      <a href="#page-chiffres" class="km-ib-item km-ib-highlight km-ib-mot-maire"><i class="fa-solid fa-user-tie"></i> Mot du Maire</a>
      <a href="{% url 'foncier_info' %}" class="km-ib-item"><i class="fa-solid fa-landmark-dome"></i> Foncier</a>
      <a href="{% url 'fiscalite' %}" class="km-ib-item"><i class="fa-solid fa-scale-balanced"></i> Fiscalit&eacute;</a>
      <div class="km-ib-social">
        <a href="#" aria-label="Facebook" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-facebook-f"></i></a>
        <a href="#" aria-label="X (Twitter)" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-x-twitter"></i></a>
        <a href="#" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-linkedin-in"></i></a>
      </div>
      <a href="tel:+221338892002" class="km-ib-item"><i class="fa-solid fa-phone"></i> +221 33 840 61 84</a>
      <a href="mailto:info@keurmassarnord.com" class="km-ib-item"><i class="fa-solid fa-envelope"></i> info@keurmassarnord.com</a>
      <span class="km-ib-item"><i class="fa-solid fa-location-dot"></i> Keur Massar Nord, Dakar</span>
      <span class="km-ib-item"><i class="fa-solid fa-clock"></i> Lun&ndash;Ven, 8h&ndash;17h</span>
      <a href="#page-chiffres" class="km-ib-item km-ib-highlight km-ib-mot-maire"><i class="fa-solid fa-user-tie"></i> Mot du Maire</a>
      <a href="{% url 'foncier_info' %}" class="km-ib-item"><i class="fa-solid fa-landmark-dome"></i> Foncier</a>
      <a href="{% url 'fiscalite' %}" class="km-ib-item"><i class="fa-solid fa-scale-balanced"></i> Fiscalit&eacute;</a>
      <div class="km-ib-social">
        <a href="#" aria-label="Facebook" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-facebook-f"></i></a>
        <a href="#" aria-label="X (Twitter)" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-x-twitter"></i></a>
        <a href="#" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-linkedin-in"></i></a>
      </div>
    </div>
  </div>'''

nouveau_html = '''  <div class="km-hero-infobar">
    <div class="km-hero-infobar-inner">
      <div class="km-ib-rotator" id="kmInfobarRotator">
        <a href="tel:+221338892002" class="km-ib-slide is-active"><i class="fa-solid fa-phone"></i> +221 33 840 61 84</a>
        <a href="mailto:info@keurmassarnord.com" class="km-ib-slide"><i class="fa-solid fa-envelope"></i> info@keurmassarnord.com</a>
        <span class="km-ib-slide"><i class="fa-solid fa-location-dot"></i> Keur Massar Nord, Dakar</span>
        <span class="km-ib-slide"><i class="fa-solid fa-clock"></i> Lun&ndash;Ven, 8h&ndash;17h</span>
        <a href="#page-chiffres" class="km-ib-slide km-ib-highlight km-ib-mot-maire"><i class="fa-solid fa-user-tie"></i> Mot du Maire</a>
        <a href="{% url 'foncier_info' %}" class="km-ib-slide"><i class="fa-solid fa-landmark-dome"></i> Foncier</a>
        <a href="{% url 'fiscalite' %}" class="km-ib-slide"><i class="fa-solid fa-scale-balanced"></i> Fiscalit&eacute;</a>
      </div>
      <div class="km-ib-social">
        <a href="#" aria-label="Facebook" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-facebook-f"></i></a>
        <a href="#" aria-label="X (Twitter)" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-x-twitter"></i></a>
        <a href="#" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-linkedin-in"></i></a>
      </div>
    </div>
  </div>'''

if 'id="kmInfobarRotator"' in contenu:
    resultats.append("HTML rotation : IGNORE (deja present)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML rotation : OK (un seul jeu d'items, en diapositives)")
else:
    resultats.append("HTML rotation : ERREUR bloc introuvable tel quel")

# ============================================================
# 3. JS : fait tourner les diapositives toutes les 3 secondes
# ============================================================
ancien_js = '''      document.querySelectorAll('.km-ib-mot-maire').forEach(function (lien) {
        lien.addEventListener('click', function (e) {
          e.preventDefault();
          document.body.classList.remove('km-hero-locked');
          var cible = document.getElementById('page-chiffres');
          if (cible) cible.scrollIntoView({ behavior: 'smooth' });
        });
      });'''

nouveau_js = '''      document.querySelectorAll('.km-ib-mot-maire').forEach(function (lien) {
        lien.addEventListener('click', function (e) {
          e.preventDefault();
          document.body.classList.remove('km-hero-locked');
          var cible = document.getElementById('page-chiffres');
          if (cible) cible.scrollIntoView({ behavior: 'smooth' });
        });
      });

      var rotateur = document.getElementById('kmInfobarRotator');
      if (rotateur) {
        var diapos = rotateur.querySelectorAll('.km-ib-slide');
        var indexDiapo = 0;
        if (diapos.length > 1) {
          setInterval(function () {
            diapos[indexDiapo].classList.remove('is-active');
            indexDiapo = (indexDiapo + 1) % diapos.length;
            diapos[indexDiapo].classList.add('is-active');
          }, 3000);
        }
      }'''

if "kmInfobarRotator" in contenu and "indexDiapo" in contenu:
    resultats.append("JS rotation : IGNORE (deja present)")
elif ancien_js in contenu:
    contenu = contenu.replace(ancien_js, nouveau_js, 1)
    resultats.append("JS rotation : OK (change de diapositive toutes les 3s)")
else:
    resultats.append("JS rotation : ERREUR point d'ancrage introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))