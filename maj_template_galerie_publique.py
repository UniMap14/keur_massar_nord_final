CHEMIN = "foncier/templates/foncier/galerie.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    <section class="gal-grid-section">
        <div class="gal-grid" id="galGrid">
            <button type="button" class="gal-card" data-src="{% static 'foncier/img/gallery/panneau-entree-commune.jpeg' %}" data-caption="Entr&eacute;e de la Commune de Keur Massar Nord">
                <div class="gal-card-img">
                    <span class="gal-card-zoom"><i class="fa-solid fa-expand"></i></span>
                    <img src="{% static 'foncier/img/gallery/panneau-entree-commune.jpeg' %}" alt="Entr&eacute;e de la Commune de Keur MassarNord">
                </div>
                <div class="gal-card-body"><h4>Entr&eacute;e de la Commune de Keur Massar Nord</h4></div>
            </button>

            <button type="button" class="gal-card" data-src="{% static 'foncier/img/gallery/mairie-batiment.jpeg' %}" data-caption="B&acirc;timent de la mairie">
                <div class="gal-card-img">
                    <span class="gal-card-zoom"><i class="fa-solid fa-expand"></i></span>
                    <img src="{% static 'foncier/img/gallery/mairie-batiment.jpeg' %}" alt="B&acirc;timent de la mairie">
                </div>
                <div class="gal-card-body"><h4>B&acirc;timent de la mairie</h4></div>
            </button>

            <button type="button" class="gal-card" data-src="{% static 'foncier/img/gallery/marche-commerces.jpg' %}" data-caption="March&eacute; et commerces anim&eacute;s">
                <div class="gal-card-img">
                    <span class="gal-card-zoom"><i class="fa-solid fa-expand"></i></span>
                    <img src="{% static 'foncier/img/gallery/marche-commerces.jpg' %}" alt="March&eacute; et commerces anim&eacute;s">
                </div>
                <div class="gal-card-body"><h4>March&eacute; et commerces anim&eacute;s</h4></div>
            </button>

            <button type="button" class="gal-card" data-src="{% static 'foncier/img/gallery/circulation-pont.jpeg' %}" data-caption="Axes routiers et circulation">
                <div class="gal-card-img">
                    <span class="gal-card-zoom"><i class="fa-solid fa-expand"></i></span>
                    <img src="{% static 'foncier/img/gallery/circulation-pont.jpeg' %}" alt="Axes routiers et circulation">
                </div>
                <div class="gal-card-body"><h4>Axes routiers et circulation</h4></div>
            </button>

            <button type="button" class="gal-card" data-src="{% static 'foncier/img/gallery/centre-services-fiscaux.jpeg' %}" data-caption="Centre des services fiscaux (DGID)">
                <div class="gal-card-img">
                    <span class="gal-card-zoom"><i class="fa-solid fa-expand"></i></span>
                    <img src="{% static 'foncier/img/gallery/centre-services-fiscaux.jpeg' %}" alt="Centre des services fiscaux (DGID)">
                </div>
                <div class="gal-card-body"><h4>Centre des services fiscaux (DGID)</h4></div>
            </button>
        </div>
    </section>'''

nouveau = '''    <section class="gal-grid-section">
        <div class="gal-grid" id="galGrid">
            {% for p in photos %}
            <button type="button" class="gal-card" data-src="{{ p.photo.url }}" data-caption="{{ p.titre }}">
                <div class="gal-card-img">
                    <span class="gal-card-zoom"><i class="fa-solid fa-expand"></i></span>
                    <img src="{{ p.photo.url }}" alt="{{ p.titre }}">
                </div>
                <div class="gal-card-body"><h4>{{ p.titre }}</h4></div>
            </button>
            {% empty %}
            <p style="grid-column:1/-1; text-align:center; color:var(--gp-brown-light); padding:40px 0;">
                Aucune photo pour le moment.
            </p>
            {% endfor %}
        </div>
    </section>'''

if "{% for p in photos %}" in contenu:
    print("IGNORE : template deja mis a jour.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : template mis a jour pour boucler sur les photos de la base.")
else:
    print("ERREUR : bloc des 5 photos introuvable tel quel.")