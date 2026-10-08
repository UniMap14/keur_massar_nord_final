# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. CSS : retour au defilement continu
# ============================================================
ancien_css = '''  .km-ticker-track-wrap{position:relative;overflow:hidden;flex:1;height:38px;}
  .km-ticker-item{
    position:absolute; inset:0; display:flex; align-items:center; gap:8px;
    padding:0 28px; color:#fff; text-decoration:none; font-size:12.5px;
    opacity:0; transform:translateX(-40px); transition:opacity .6s ease, transform .6s ease;
    pointer-events:none;
  }
  .km-ticker-item.is-active{ opacity:1; transform:translateX(0); pointer-events:auto; }
  .km-ticker-item.is-leaving{ opacity:0; transform:translateX(40px); }
  .km-ticker-item:hover{color:var(--km-gold-light);}
  .km-ticker-cat{ color:rgba(255,255,255,.6); font-weight:700; text-transform:uppercase; font-size:10.5px; }
  .km-ticker-date{color:var(--km-gold);font-weight:700;}'''

nouveau_css = '''  .km-ticker-track-wrap{overflow:hidden;flex:1;display:flex;align-items:center;}
  .km-ticker-track{display:flex;gap:0;white-space:nowrap;animation:kmTickerScroll 40s linear infinite;}
  .km-ticker-track:hover{animation-play-state:paused;}
  .km-ticker-item{
    color:#fff;text-decoration:none;font-size:12.5px;padding:10px 28px;
    border-right:1px solid rgba(255,255,255,0.12);display:inline-flex;align-items:center;gap:8px;
  }
  .km-ticker-item:hover{color:var(--km-gold-light);}
  .km-ticker-cat{ color:rgba(255,255,255,.6); font-weight:700; text-transform:uppercase; font-size:10.5px; }
  .km-ticker-date{color:var(--km-gold);font-weight:700;}
  @keyframes kmTickerScroll{
    from{transform:translateX(0);}
    to{transform:translateX(-50%);}
  }'''

if "kmTickerScroll" in contenu and ".km-ticker-item.is-leaving" not in contenu:
    resultats.append("CSS : IGNORE (deja revenu en arriere)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS : OK (defilement continu restaure)")
else:
    resultats.append("CSS : ERREUR introuvable")

# ============================================================
# 2. HTML : retour a la boucle dupliquee
# ============================================================
ancien_html = '''<div class="km-ticker">
  <div class="km-ticker-label"><i class="fa-solid fa-tower-broadcast"></i> En direct</div>
  <div class="km-ticker-track-wrap" id="kmTickerRotator">
    {% for a in actualites_ticker %}
      <a href="{% url 'actualite_detail' a.pk %}" class="km-ticker-item{% if forloop.first %} is-active{% endif %}">
        <span class="km-ticker-date">{{ a.date_publication|date:"d/m" }}</span> {{ a.titre }}
      </a>
    {% endfor %}
  </div>'''

nouveau_html = '''<div class="km-ticker">
  <div class="km-ticker-label"><i class="fa-solid fa-tower-broadcast"></i> En direct</div>
  <div class="km-ticker-track-wrap">
    <div class="km-ticker-track">
      {% for a in actualites_ticker %}
        <a href="{% url 'actualite_detail' a.pk %}" class="km-ticker-item">
          <span class="km-ticker-date">{{ a.date_publication|date:"d/m" }}</span> {{ a.titre }}
        </a>
      {% endfor %}
      {% for a in actualites_ticker %}
        <a href="{% url 'actualite_detail' a.pk %}" class="km-ticker-item" aria-hidden="true">
          <span class="km-ticker-date">{{ a.date_publication|date:"d/m" }}</span> {{ a.titre }}
        </a>
      {% endfor %}
    </div>
  </div>'''

if 'id="kmTickerRotator"' not in contenu:
    resultats.append("HTML : IGNORE (deja revenu en arriere)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML : OK (boucle dupliquee restauree)")
else:
    resultats.append("HTML : ERREUR introuvable")

# ============================================================
# 3. JS : retire le bloc de rotation du ticker
# ============================================================
ancien_js = '''      var tickerRotateur = document.getElementById('kmTickerRotator');
      if (tickerRotateur) {
        var itemsTicker = tickerRotateur.querySelectorAll('.km-ticker-item');
        var indexTicker = 0;
        if (itemsTicker.length > 1) {
          setInterval(function () {
            var ancienItem = itemsTicker[indexTicker];
            ancienItem.classList.remove('is-active');
            ancienItem.classList.add('is-leaving');

            indexTicker = (indexTicker + 1) % itemsTicker.length;
            itemsTicker[indexTicker].classList.add('is-active');

            setTimeout(function () {
              ancienItem.classList.remove('is-leaving');
            }, 650);
          }, 3000);
        }
      }

      var rotateur = document.getElementById('kmInfobarRotator');'''

nouveau_js = '''      var rotateur = document.getElementById('kmInfobarRotator');'''

if "tickerRotateur" not in contenu:
    resultats.append("JS : IGNORE (deja revenu en arriere)")
elif ancien_js in contenu:
    contenu = contenu.replace(ancien_js, nouveau_js, 1)
    resultats.append("JS : OK (bloc de rotation du ticker retire)")
else:
    resultats.append("JS : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))