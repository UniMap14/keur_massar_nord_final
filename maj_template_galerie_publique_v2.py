# -*- coding: utf-8 -*-
import re

CHEMIN = "foncier/templates/foncier/galerie.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "{% for p in photos %}" in contenu:
    print("IGNORE : template deja mis a jour.")
else:
    debut_marqueur = '<div class="gal-grid" id="galGrid">'
    idx_debut = contenu.find(debut_marqueur)

    if idx_debut == -1:
        print("ERREUR : marqueur de debut '<div class=\"gal-grid\" id=\"galGrid\">' introuvable.")
    else:
        # Cherche le </div> de fermeture correspondant, en comptant les
        # ouvertures/fermetures de <div a partir du marqueur de debut
        # (pour ne pas s'arreter au premier </div> imbrique).
        pos = idx_debut + len(debut_marqueur)
        profondeur = 1
        fin_contenu = None
        for m in re.finditer(r'<div\b|</div>', contenu[pos:]):
            if m.group() == '</div>':
                profondeur -= 1
            else:
                profondeur += 1
            if profondeur == 0:
                fin_contenu = pos + m.start()
                fin_fermeture = pos + m.end()
                break

        if fin_contenu is None:
            print("ERREUR : impossible de trouver la fermeture </div> correspondante.")
        else:
            nouveau_interieur = '''
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
        '''
            contenu_final = contenu[:idx_debut + len(debut_marqueur)] + nouveau_interieur + contenu[fin_contenu:]
            with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
                f.write(contenu_final)
            print("OK : template mis a jour pour boucler sur les photos de la base.")