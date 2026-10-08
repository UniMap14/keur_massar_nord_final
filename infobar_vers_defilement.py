# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. CSS : remplace la rotation par le defilement continu
# ============================================================
ancien_css = '''  .km-ib-rotator{ position:relative; height:18px; flex:1; max-width:420px; overflow:hidden; }
  .km-ib-slide{
    position:absolute; inset:0; display:flex; align-items:center; justify-content:center; gap:7px;
    opacity:0; transform:translateX(40px); transition:opacity .6s ease, transform .6s ease;
    pointer-events:none;
  }
  .km-ib-slide.is-active{ opacity:1; transform:translateX(0); pointer-events:auto; }
  .km-ib-slide.is-leaving{ opacity:0; transform:translateX(-40px); }'''

nouveau_css = '''  .km-hero-infobar{ overflow:hidden; }
  .km-hero-infobar-inner{
    display:flex; align-items:center; gap:30px;
    padding:14px 0; white-space:nowrap; width:max-content;
    animation: kmInfobarScroll 26s linear infinite;
  }
  .km-hero-infobar:hover .km-hero-infobar-inner{ animation-play-state:paused; }
  @keyframes kmInfobarScroll{
    from{ transform:translateX(0); }
    to{ transform:translateX(-50%); }
  }
  .km-ib-item{
    display:inline-flex; align-items:center; gap:7px;
    font-size:12.5px; color:rgba(255,255,255,.85); text-decoration:none; white-space:nowrap;
    transition:color .2s ease;
  }
  .km-ib-item i{ color:var(--km-gold); font-size:11px; }
  .km-ib-item:hover{ color:var(--km-gold-light); }
  .km-ib-highlight{ font-weight:700; color:var(--km-gold-light); }'''

if "kmInfobarScroll" in contenu:
    resultats.append("CSS : IGNORE (deja en defilement continu)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS : OK (defilement continu applique)")
else:
    resultats.append("CSS : ERREUR introuvable")

# ============================================================
# 2. HTML : remplace les diapositives par des items dupliques
# ============================================================
ancien_html = '''      <div class="km-ib-rotator" id="kmInfobarRotator">
        <a href="tel:+221338892002" class="km-ib-slide is-active"><i class="fa-solid fa-phone"></i> +221 33 840 61 84</a>
        <a href="mailto:info@keurmassarnord.com" class="km-ib-slide"><i class="fa-solid fa-envelope"></i> info@keurmassarnord.com</a>
        <span class="km-ib-slide"><i class="fa-solid fa-location-dot"></i> Keur Massar Nord, Dakar</span>
        <span class="km-ib-slide"><i class="fa-solid fa-clock"></i> Lun&ndash;Ven, 8h&ndash;17h</span>
        <a href="#page-chiffres" class="km-ib-slide km-ib-highlight km-ib-mot-maire"><i class="fa-solid fa-user-tie"></i> Mot du Maire</a>
        <a href="{% url 'foncier_info' %}" class="km-ib-slide"><i class="fa-solid fa-landmark-dome"></i> Foncier</a>
        <a href="{% url 'fiscalite' %}" class="km-ib-slide"><i class="fa-solid fa-scale-balanced"></i> Fiscalit&eacute;</a>
      </div>'''

def bloc_items():
    return '''      <a href="tel:+221338892002" class="km-ib-item"><i class="fa-solid fa-phone"></i> +221 33 840 61 84</a>
      <a href="mailto:info@keurmassarnord.com" class="km-ib-item"><i class="fa-solid fa-envelope"></i> info@keurmassarnord.com</a>
      <span class="km-ib-item"><i class="fa-solid fa-location-dot"></i> Keur Massar Nord, Dakar</span>
      <span class="km-ib-item"><i class="fa-solid fa-clock"></i> Lun&ndash;Ven, 8h&ndash;17h</span>
      <a href="#page-chiffres" class="km-ib-item km-ib-highlight km-ib-mot-maire"><i class="fa-solid fa-user-tie"></i> Mot du Maire</a>
      <a href="{% url 'foncier_info' %}" class="km-ib-item"><i class="fa-solid fa-landmark-dome"></i> Foncier</a>
      <a href="{% url 'fiscalite' %}" class="km-ib-item"><i class="fa-solid fa-scale-balanced"></i> Fiscalit&eacute;</a>'''

nouveau_html = bloc_items() + '\n' + bloc_items()

if 'id="kmInfobarRotator"' not in contenu:
    resultats.append("HTML : IGNORE (deja en defilement continu)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML : OK (items dupliques pour boucle continue)")
else:
    resultats.append("HTML : ERREUR introuvable")

# ============================================================
# 3. JS : retire la logique de rotation (plus necessaire),
#    garde le clic sur Mot du Maire pour debloquer le scroll
# ============================================================
ancien_js = '''      var rotateur = document.getElementById('kmInfobarRotator');
      if (rotateur) {
        var diapos = rotateur.querySelectorAll('.km-ib-slide');
        var indexDiapo = 0;
        if (diapos.length > 1) {
          setInterval(function () {
            var ancienneDiapo = diapos[indexDiapo];
            ancienneDiapo.classList.remove('is-active');
            ancienneDiapo.classList.add('is-leaving');

            indexDiapo = (indexDiapo + 1) % diapos.length;
            diapos[indexDiapo].classList.add('is-active');

            setTimeout(function () {
              ancienneDiapo.classList.remove('is-leaving');
            }, 650);
          }, 3000);
        }
      }'''

nouveau_js = ''

if "kmInfobarRotator" not in contenu or "var rotateur = document.getElementById('kmInfobarRotator')" not in contenu:
    resultats.append("JS : IGNORE (deja retire ou absent)")
elif ancien_js in contenu:
    contenu = contenu.replace(ancien_js, nouveau_js, 1)
    resultats.append("JS : OK (logique de rotation retiree)")
else:
    resultats.append("JS : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))