# -*- coding: utf-8 -*-
"""
Change le comportement initial de la Cartotheque : au chargement, aucune
carte n'est affichee. L'utilisateur doit cliquer sur un filtre (un theme,
ou "Toutes" pour tout voir) ou taper une recherche pour voir des cartes.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/cartotheque.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

def remplacer(ancien, nouveau, marqueur_deja_fait):
    global contenu, remplacements_ok
    if marqueur_deja_fait in contenu:
        return
    if ancien not in contenu:
        erreurs.append(f"ancre introuvable : {ancien[:70]}...")
        return
    contenu = contenu.replace(ancien, nouveau, 1)
    remplacements_ok += 1

# 1) CSS : etendre le style partage aux 3 messages d'etat vide
remplacer(
    '''    .carto-empty, .carto-no-results{
        text-align:center; padding:70px 20px; color:var(--cp-brown-light);
    }
    .carto-empty i, .carto-no-results i{ font-size:32px; color:var(--cp-gold); margin-bottom:16px; display:block; }
    .carto-no-results{ display:none; }
    .carto-no-results.visible{ display:block; }''',
    '''    .carto-empty, .carto-no-results, .carto-choisir-filtre{
        text-align:center; padding:70px 20px; color:var(--cp-brown-light);
    }
    .carto-empty i, .carto-no-results i, .carto-choisir-filtre i{ font-size:32px; color:var(--cp-gold); margin-bottom:16px; display:block; }
    .carto-no-results{ display:none; }
    .carto-no-results.visible{ display:block; }
    .carto-choisir-filtre{ display:none; grid-column:1/-1; }
    .carto-choisir-filtre.visible{ display:block; }''',
    'carto-choisir-filtre{ display:none; grid-column:1/-1; }'
)

# 2) HTML : le chip "Toutes" n'est plus actif par defaut
remplacer(
    '''<button type="button" class="carto-filtre-chip active" data-theme-filtre="">Toutes</button>''',
    '''<button type="button" class="carto-filtre-chip" data-theme-filtre="">Toutes</button>''',
    '<button type="button" class="carto-filtre-chip" data-theme-filtre="">Toutes</button>'
)

# 3) HTML : ajout du message "choisir un filtre"
remplacer(
    '''        <div class="carto-no-results" id="cartoNoResults">
            <i class="fa-solid fa-magnifying-glass"></i>
            Aucune carte ne correspond \u00e0 votre recherche.
        </div>
    </div>''',
    '''        <div class="carto-no-results" id="cartoNoResults">
            <i class="fa-solid fa-magnifying-glass"></i>
            Aucune carte ne correspond \u00e0 votre recherche.
        </div>

        <div class="carto-choisir-filtre visible" id="cartoChoisirFiltre">
            <i class="fa-solid fa-filter"></i>
            Choisissez un th\u00e8me ci-dessus (ou \u00ab\u00a0Toutes\u00a0\u00bb) pour afficher les cartes.
        </div>
    </div>''',
    'id="cartoChoisirFiltre"'
)

# 4) JS : logique "aucun filtre choisi au depart"
remplacer(
    '''    const chipsFiltre = document.querySelectorAll('.carto-filtre-chip');
    let themeActif = '';

    function appliquerRecherche() {
        const requete = champRecherche ? champRecherche.value.trim().toLowerCase() : '';
        let visibles = 0;

        toutesLesCartes.forEach(function (carte) {''',
    '''    const chipsFiltre = document.querySelectorAll('.carto-filtre-chip');
    const messageChoisirFiltre = document.getElementById('cartoChoisirFiltre');
    let themeActif = '';
    let aucunFiltreChoisi = true;

    function appliquerRecherche() {
        const requete = champRecherche ? champRecherche.value.trim().toLowerCase() : '';
        let visibles = 0;

        if (aucunFiltreChoisi) {
            toutesLesCartes.forEach(function (carte) { carte.classList.add('carto-hidden'); });
            if (messageChoisirFiltre) messageChoisirFiltre.classList.add('visible');
            if (messageAucunResultat) messageAucunResultat.classList.remove('visible');
            if (compteurResultats) compteurResultats.textContent = '';
            if (boutonEffacer) boutonEffacer.classList.toggle('visible', requete !== '');
            return;
        }
        if (messageChoisirFiltre) messageChoisirFiltre.classList.remove('visible');

        toutesLesCartes.forEach(function (carte) {''',
    'let aucunFiltreChoisi = true;'
)

# 5) JS : un clic sur un chip ou une saisie de recherche = un choix fait
remplacer(
    '''    chipsFiltre.forEach(function (chip) {
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
    }''',
    '''    chipsFiltre.forEach(function (chip) {
        chip.addEventListener('click', function () {
            aucunFiltreChoisi = false;
            themeActif = chip.getAttribute('data-theme-filtre') || '';
            chipsFiltre.forEach(function (c) { c.classList.toggle('active', c === chip); });
            appliquerRecherche();
        });
    });

    if (champRecherche) {
        champRecherche.addEventListener('input', function () {
            aucunFiltreChoisi = false;
            appliquerRecherche();
        });
        boutonEffacer.addEventListener('click', function () {
            champRecherche.value = '';
            aucunFiltreChoisi = false;
            appliquerRecherche();
            champRecherche.focus();
        });
    }''',
    'aucunFiltreChoisi = false;\n            themeActif ='
)

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")