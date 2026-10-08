# -*- coding: utf-8 -*-
CHEMIN = "foncier/static/foncier/js/voice-guide.js"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien = '''        sections = [];

        /*
         * On sélectionne uniquement les parties utiles
         * de la page d'accueil.
         */

        const selectors = [
            {
                selector: '.km-hero',
                intro: 'Bienvenue sur le portail officiel de Keur Massar Nord.'
            },
            {
                selector: '.km-quick-section',
                intro: 'Voici les informations essentielles sur la commune.'
            },
            {
                selector: '.histoire-layout',
                intro: 'Découvrez maintenant l\u2019histoire de Keur Massar Nord.'
            },
            {
                selector: '.services-section',
                intro: 'Cette plateforme propose plusieurs services numériques.'
            },
            {
                selector: '.km-dash-section',
                intro: 'Voici un aperçu des infrastructures, des signalements citoyens et des actualités.'
            },
            {
                selector: '.security-section',
                intro: 'La plateforme présente également les garanties de sécurité et de fiabilité des données.'
            },
            {
                selector: '.page-section',
                intro: 'Vous pouvez également explorer la commune depuis le géoportail.'
            },
            {
                selector: '.mayor-section',
                intro: 'Voici le message du maire de Keur Massar Nord.'
            },
            {
                selector: '.gallery-grid',
                intro: 'Enfin, découvrez la commune à travers sa galerie d\u2019images.'
            }
        ];

        selectors.forEach(function (item) {'''

nouveau = '''        sections = [];

        /*
         * Jeux de selecteurs par page. "accueil" couvre la page d'accueil,
         * les autres cles couvrent des pages dont on connait les classes
         * CSS. "defaut" sert de filet de securite generique pour TOUTE
         * autre page du site, afin que le guide ne reste jamais muet.
         */
        const cheminActuel = window.location.pathname;

        const jeuxDeSelecteurs = {
            accueil: [
                { selector: '.km-hero', intro: 'Bienvenue sur le portail officiel de Keur Massar Nord.' },
                { selector: '.km-quick-section', intro: 'Voici les informations essentielles sur la commune.' },
                { selector: '.histoire-layout', intro: 'Découvrez maintenant l\u2019histoire de Keur Massar Nord.' },
                { selector: '.services-section', intro: 'Cette plateforme propose plusieurs services numériques.' },
                { selector: '.km-dash-section', intro: 'Voici un aperçu des infrastructures, des signalements citoyens et des actualités.' },
                { selector: '.security-section', intro: 'La plateforme présente également les garanties de sécurité et de fiabilité des données.' },
                { selector: '.page-section', intro: 'Vous pouvez également explorer la commune depuis le géoportail.' },
                { selector: '.mayor-section', intro: 'Voici le message du maire de Keur Massar Nord.' },
                { selector: '.gallery-grid', intro: 'Enfin, découvrez la commune à travers sa galerie d\u2019images.' }
            ],
            galerie: [
                { selector: '.gal-grid-section', intro: 'Voici la galerie de photos de la commune.' }
            ],
            cartotheque: [
                { selector: '.carto-list', intro: 'Voici les cartes thématiques disponibles, avec leur explication.' }
            ],
            foncier: [
                { selector: '.fi-section', intro: '' }
            ],
            recherche: [
                { selector: '.rg-results', intro: 'Voici les résultats de votre recherche.' }
            ]
        };

        let cleJeu = 'defaut';
        if (cheminActuel === '/' || cheminActuel.indexOf('/accueil') !== -1) cleJeu = 'accueil';
        else if (cheminActuel.indexOf('/galerie') !== -1) cleJeu = 'galerie';
        else if (cheminActuel.indexOf('/cartotheque') !== -1) cleJeu = 'cartotheque';
        else if (cheminActuel.indexOf('/foncier-info') !== -1) cleJeu = 'foncier';
        else if (cheminActuel.indexOf('/recherche') !== -1) cleJeu = 'recherche';

        let selectors;

        if (cleJeu !== 'defaut' && jeuxDeSelecteurs[cleJeu]) {
            selectors = jeuxDeSelecteurs[cleJeu];
        } else {
            /*
             * Filet de securite generique : lit le titre principal puis
             * chaque <section> visible de la page, quelle qu'elle soit.
             */
            selectors = [];
            if (document.querySelector('h1')) {
                selectors.push({ selector: 'h1', intro: '' });
            }
            document.querySelectorAll('main section, .main-content section, section').forEach(function (sec, idx) {
                sec.setAttribute('data-vg-idx', idx);
                selectors.push({ selector: '[data-vg-idx="' + idx + '"]', intro: '' });
            });
        }

        selectors.forEach(function (item) {'''

if "jeuxDeSelecteurs" in contenu:
    resultats.append("buildGuide() : IGNORE (deja generalise)")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    resultats.append("buildGuide() : OK (fonctionne maintenant sur toutes les pages)")
else:
    resultats.append("buildGuide() : ERREUR introuvable (verifie l'encodage exact du fichier)")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))