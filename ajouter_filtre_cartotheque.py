# -*- coding: utf-8 -*-
"""
Ajoute des boutons de filtre par theme au-dessus des cartes de la
cartotheque, combines avec la recherche texte deja en place. S'appuie
sur c.theme deja calcule par la vue -- pas de migration necessaire.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/cartotheque.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) data-theme sur chaque carte
# ------------------------------------------------------------------
ANCIEN_CARTE = '<div class="carto-card" data-search="{{ c.titre|lower }} {{ c.explication|lower }}">'
NOUVEAU_CARTE = '<div class="carto-card" data-search="{{ c.titre|lower }} {{ c.explication|lower }}" data-theme="{{ c.theme }}">'

if NOUVEAU_CARTE in contenu:
    pass
elif ANCIEN_CARTE not in contenu:
    erreurs.append("div carto-card introuvable")
else:
    contenu = contenu.replace(ANCIEN_CARTE, NOUVEAU_CARTE)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) Barre de filtres, dans la toolbar, sous le compteur de resultats
# ------------------------------------------------------------------
ANCIEN_TOOLBAR = '''        <div class="carto-results-count" id="cartoResultsCount"></div>
    </div>
    {% endif %}'''

NOUVEAU_TOOLBAR = '''        <div class="carto-results-count" id="cartoResultsCount"></div>
        <div class="carto-filtres" id="cartoFiltres">
            <button type="button" class="carto-filtre-chip active" data-theme-filtre="">Toutes</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Relief &amp; pentes">Relief &amp; pentes</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Hydrologie">Hydrologie</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Infrastructures">Infrastructures</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Éducation">Éducation</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Santé">Santé</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Analyse territoriale">Analyse territoriale</button>
        </div>
    </div>
    {% endif %}'''

if 'id="cartoFiltres"' in contenu:
    pass
elif ANCIEN_TOOLBAR not in contenu:
    erreurs.append("bloc toolbar introuvable")
else:
    contenu = contenu.replace(ANCIEN_TOOLBAR, NOUVEAU_TOOLBAR, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 3) CSS des chips
# ------------------------------------------------------------------
ANCIEN_CSS_ANCRE = '    .carto-empty, .carto-no-results{'
NOUVEAU_CSS = '''    .carto-filtres{ display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-top:6px; }
    .carto-filtre-chip{
        border:1.5px solid var(--cp-border); background:#fff; color:var(--cp-brown-light);
        font-size:12.5px; font-weight:700; padding:7px 15px; border-radius:999px; cursor:pointer;
        transition: all .15s ease;
    }
    .carto-filtre-chip:hover{ background:var(--cp-cream-2); }
    .carto-filtre-chip.active{ background:var(--cp-brown-dark); border-color:var(--cp-brown-dark); color:#fff; }

    .carto-empty, .carto-no-results{'''

if '.carto-filtre-chip{' in contenu:
    pass
elif ANCIEN_CSS_ANCRE not in contenu:
    erreurs.append("ancre CSS carto-empty introuvable")
else:
    contenu = contenu.replace(ANCIEN_CSS_ANCRE, NOUVEAU_CSS, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 4) JS : combine recherche texte + filtre theme
# ------------------------------------------------------------------
ANCIEN_JS = '''    // ---- Recherche texte simple (titre + explication) ----
    const champRecherche = document.getElementById('cartoSearchInput');
    const boutonEffacer = document.getElementById('cartoSearchClear');
    const compteurResultats = document.getElementById('cartoResultsCount');
    const messageAucunResultat = document.getElementById('cartoNoResults');
    const totalCartes = toutesLesCartes.length;

    function appliquerRecherche() {
        const requete = champRecherche.value.trim().toLowerCase();
        let visibles = 0;

        toutesLesCartes.forEach(function (carte) {
            const texte = carte.getAttribute('data-search') || '';
            const correspond = requete === '' || texte.includes(requete);
            carte.classList.toggle('carto-hidden', !correspond);
            if (correspond) {
                visibles++;
                carte.classList.add('carto-visible');
            }
        });

        boutonEffacer.classList.toggle('visible', requete !== '');

        if (requete === '') {
            compteurResultats.textContent = '';
        } else {
            compteurResultats.innerHTML = '<strong>' + visibles + '</strong> carte' +
                (visibles !== 1 ? 's' : '') + ' sur ' + totalCartes;
        }

        if (messageAucunResultat) {
            messageAucunResultat.classList.toggle('visible', requete !== '' && visibles === 0);
        }
    }

    if (champRecherche) {
        champRecherche.addEventListener('input', appliquerRecherche);
        boutonEffacer.addEventListener('click', function () {
            champRecherche.value = '';
            appliquerRecherche();
            champRecherche.focus();
        });
    }'''

NOUVEAU_JS = '''    // ---- Recherche texte + filtre par theme (chips) ----
    const champRecherche = document.getElementById('cartoSearchInput');
    const boutonEffacer = document.getElementById('cartoSearchClear');
    const compteurResultats = document.getElementById('cartoResultsCount');
    const messageAucunResultat = document.getElementById('cartoNoResults');
    const totalCartes = toutesLesCartes.length;
    const chipsFiltre = document.querySelectorAll('.carto-filtre-chip');
    let themeActif = '';

    function appliquerRecherche() {
        const requete = champRecherche ? champRecherche.value.trim().toLowerCase() : '';
        let visibles = 0;

        toutesLesCartes.forEach(function (carte) {
            const texte = carte.getAttribute('data-search') || '';
            const correspondTexte = requete === '' || texte.includes(requete);
            const correspondTheme = themeActif === '' || carte.getAttribute('data-theme') === themeActif;
            const correspond = correspondTexte && correspondTheme;
            carte.classList.toggle('carto-hidden', !correspond);
            if (correspond) {
                visibles++;
                carte.classList.add('carto-visible');
            }
        });

        if (boutonEffacer) boutonEffacer.classList.toggle('visible', requete !== '');

        const filtreActif = requete !== '' || themeActif !== '';
        if (!filtreActif) {
            compteurResultats.textContent = '';
        } else {
            compteurResultats.innerHTML = '<strong>' + visibles + '</strong> carte' +
                (visibles !== 1 ? 's' : '') + ' sur ' + totalCartes;
        }

        if (messageAucunResultat) {
            messageAucunResultat.classList.toggle('visible', filtreActif && visibles === 0);
        }
    }

    chipsFiltre.forEach(function (chip) {
        chip.addEventListener('click', function () {
            themeActif = chip.getAttribute('data-theme-filtre') || '';
            chipsFiltre.forEach(function (c) { c.classList.toggle('active', c === chip); });
            appliquerRecherche();
        });
    });

    if (champRecherche) {
        champRecherche.addEventListener('input', appliquerRecherche);
        boutonEffacer.addEventListener('click', function () {
            champRecherche.value = '';
            appliquerRecherche();
            champRecherche.focus();
        });
    }'''

if 'themeActif' in contenu:
    pass
elif ANCIEN_JS not in contenu:
    erreurs.append("bloc JS de recherche introuvable tel quel")
else:
    contenu = contenu.replace(ANCIEN_JS, NOUVEAU_JS, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")