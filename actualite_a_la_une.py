CHEMIN = "foncier/templates/foncier/actualites_liste.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- 1. CSS de la carte "a la une" ---
ancien_css = '''  .actu-empty i { font-size: 30px; color: var(--gold); margin-bottom: 14px; display: block; }
</style>'''

nouveau_css = '''  .actu-empty i { font-size: 30px; color: var(--gold); margin-bottom: 14px; display: block; }

  /* ===== A LA UNE ===== */
  .actu-une {
    display: grid; grid-template-columns: 1.1fr 1fr; gap: 0;
    background: #fff; border: 1px solid var(--border); border-radius: var(--radius);
    box-shadow: 0 14px 34px rgba(0,0,0,0.08); overflow: hidden;
    text-decoration: none; color: inherit; margin: 40px 0 10px;
  }
  .actu-une-img { position: relative; min-height: 320px; background: var(--off-white, #f4f0e8); }
  .actu-une-img img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .actu-une-img .news-img-icon { font-size: 46px; }
  .actu-une-badge {
    position: absolute; top: 18px; left: 18px; background: var(--gold, #c9982e); color: #fff;
    font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em;
    padding: 6px 14px; border-radius: 999px;
  }
  .actu-une-body { padding: 36px 40px; display: flex; flex-direction: column; justify-content: center; }
  .actu-une-date { font-size: 12.5px; color: var(--ink-quiet, #6f6a5e); margin-bottom: 10px; }
  .actu-une-body h2 { font-size: 24px; line-height: 1.3; margin: 0 0 14px; color: var(--text); }
  .actu-une-body p { font-size: 14.5px; color: var(--ink-quiet, #6f6a5e); line-height: 1.6; margin: 0 0 18px; }
  .actu-une-link { font-weight: 700; font-size: 13.5px; color: var(--green-dark); display: inline-flex; align-items: center; gap: 8px; }
  .actu-une:hover .actu-une-link { text-decoration: underline; }

  @media (max-width: 800px) {
    .actu-une { grid-template-columns: 1fr; }
    .actu-une-img { min-height: 220px; }
    .actu-une-body { padding: 26px 24px; }
  }
</style>'''

if ".actu-une {" in contenu:
    resultats.append("CSS : IGNORE (deja present)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("CSS : OK")
else:
    resultats.append("CSS : ERREUR introuvable")

# --- 2. Bloc "a la une" + exclusion du reste de la grille ---
ancien_html = '''  <p class="actu-count">{{ page_obj.paginator.count }} actualité{{ page_obj.paginator.count|pluralize }} trouvée{{ page_obj.paginator.count|pluralize }}</p>

  <div class="news-grid">
    {% for actu in page_obj %}'''

nouveau_html = '''  {% if page_obj.number == 1 and not q and not categorie and page_obj %}
    {% with une=page_obj.object_list.0 %}
    <a href="{% url 'actualite_detail' une.pk %}" class="actu-une">
      <div class="actu-une-img">
        <span class="actu-une-badge">À la une</span>
        {% if une.photo %}
          <img src="{{ une.photo.url }}" alt="">
        {% else %}
          <i class="fa-solid fa-newspaper news-img-icon"></i>
        {% endif %}
      </div>
      <div class="actu-une-body">
        <div class="actu-une-date"><i class="fa-solid fa-calendar"></i> {{ une.date_publication|date:"d F Y" }} · {{ une.get_categorie_display }}</div>
        <h2>{{ une.titre }}</h2>
        <p>{{ une.chapo }}</p>
        <span class="actu-une-link">Lire l'article <i class="fa-solid fa-arrow-right"></i></span>
      </div>
    </a>
    {% endwith %}
  {% endif %}

  <p class="actu-count">{{ page_obj.paginator.count }} actualité{{ page_obj.paginator.count|pluralize }} trouvée{{ page_obj.paginator.count|pluralize }}</p>

  <div class="news-grid">
    {% for actu in page_obj %}
    {% if not forloop.first or page_obj.number != 1 or q or categorie %}'''

if "À la une</span>" in contenu:
    resultats.append("HTML : IGNORE (deja present)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("HTML : OK")
else:
    resultats.append("HTML : ERREUR introuvable")

# --- 3. Fermeture du {% if %} juste avant {% empty %} ---
ancien_fermeture = '''        <p>{{ actu.chapo }}</p>
      </div>
    </a>
    {% empty %}'''

nouveau_fermeture = '''        <p>{{ actu.chapo }}</p>
      </div>
    </a>
    {% endif %}
    {% empty %}'''

if contenu.count("{% endif %}\n    {% empty %}") >= 1:
    resultats.append("Fermeture if : IGNORE (deja present)")
elif ancien_fermeture in contenu:
    contenu = contenu.replace(ancien_fermeture, nouveau_fermeture, 1)
    resultats.append("Fermeture if : OK")
else:
    resultats.append("Fermeture if : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))