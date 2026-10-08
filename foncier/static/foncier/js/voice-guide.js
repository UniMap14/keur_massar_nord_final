(function () {
    'use strict';

    const STORAGE_KEY = 'kmsn_voice_enabled';

    let btn = null;
    let icon = null;
    let tooltip = null;

    let currentIndex = 0;
    let isReadingGuide = false;
    let sections = [];

    // ---------------------------------------------------------
    // OUTILS
    // ---------------------------------------------------------

    function isSupported() {
        return 'speechSynthesis' in window &&
               'SpeechSynthesisUtterance' in window;
    }

    function isEnabled() {
        return localStorage.getItem(STORAGE_KEY) === '1';
    }

    function setEnabled(value) {
        localStorage.setItem(STORAGE_KEY, value ? '1' : '0');
    }

    function getFrenchVoice() {
        if (!isSupported()) return null;

        const voices = window.speechSynthesis.getVoices();

        return (
            voices.find(v => v.lang === 'fr-FR') ||
            voices.find(v => v.lang === 'fr') ||
            voices.find(v => v.lang && v.lang.toLowerCase().startsWith('fr'))
        );
    }

    function cleanText(text) {
        return (text || '')
            .replace(/\s+/g, ' ')
            .replace(/\s+([,.!?;:])/g, '$1')
            .trim();
    }

    function updateButton(state) {
        if (!btn || !icon || !tooltip) return;

        icon.classList.remove(
            'fa-volume-high',
            'fa-volume-xmark',
            'fa-pause',
            'fa-play'
        );

        btn.classList.toggle('speaking', state === 'speaking');

        if (!isEnabled()) {
            icon.classList.add('fa-volume-xmark');
            tooltip.textContent = 'Activer le guide vocal';
            btn.setAttribute('aria-label', 'Activer le guide vocal');
        }
        else if (state === 'speaking') {
            icon.classList.add('fa-pause');
            tooltip.textContent = 'Mettre en pause';
            btn.setAttribute('aria-label', 'Mettre en pause');
        }
        else if (state === 'paused') {
            icon.classList.add('fa-play');
            tooltip.textContent = 'Reprendre le guide vocal';
            btn.setAttribute('aria-label', 'Reprendre le guide vocal');
        }
        else {
            icon.classList.add('fa-volume-high');
            tooltip.textContent = 'Écouter la page';
            btn.setAttribute('aria-label', 'Écouter la page');
        }
    }

    // ---------------------------------------------------------
    // CONSTRUCTION DU GUIDE
    // ---------------------------------------------------------

    function buildGuide() {
        sections = [];

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
                { selector: '.histoire-layout', intro: 'Découvrez maintenant l’histoire de Keur Massar Nord.' },
                { selector: '.services-section', intro: 'Cette plateforme propose plusieurs services numériques.' },
                { selector: '.km-dash-section', intro: 'Voici un aperçu des infrastructures, des signalements citoyens et des actualités.' },
                { selector: '.security-section', intro: 'La plateforme présente également les garanties de sécurité et de fiabilité des données.' },
                { selector: '.page-section', intro: 'Vous pouvez également explorer la commune depuis le géoportail.' },
                { selector: '.mayor-section', intro: 'Voici le message du maire de Keur Massar Nord.' },
                { selector: '.gallery-grid', intro: 'Enfin, découvrez la commune à travers sa galerie d’images.' }
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

        selectors.forEach(function (item) {
            const element = document.querySelector(item.selector);

            if (!element) return;

            let text = cleanText(element.innerText);

            if (!text) return;

            sections.push({
                element: element,
                text: item.intro + ' ' + text
            });
        });

        console.log('[VoiceGuide] Sections trouvées :', sections.length);
    }

    // ---------------------------------------------------------
    // LECTURE D'UNE SECTION
    // ---------------------------------------------------------

    function speakCurrentSection() {
        if (!isSupported()) return;

        if (!sections.length) {
            buildGuide();
        }

        if (!sections.length) {
            console.warn('[VoiceGuide] Aucune section trouvée.');
            return;
        }

        if (currentIndex >= sections.length) {
            finishGuide();
            return;
        }

        const section = sections[currentIndex];

        window.speechSynthesis.cancel();

        highlightSection(section.element);

        const utterance = new SpeechSynthesisUtterance(section.text);

        utterance.lang = 'fr-FR';
        utterance.rate = 0.95;
        utterance.pitch = 1;

        const voice = getFrenchVoice();

        if (voice) {
            utterance.voice = voice;
        }

        utterance.onstart = function () {
            updateButton('speaking');
        };

        utterance.onend = function () {
            if (!isReadingGuide) return;

            currentIndex++;

            setTimeout(function () {
                speakCurrentSection();
            }, 400);
        };

        utterance.onerror = function (event) {
            console.warn('[VoiceGuide] Erreur :', event);

            isReadingGuide = false;
            updateButton('idle');
        };

        window.speechSynthesis.speak(utterance);
    }

    // ---------------------------------------------------------
    // MISE EN ÉVIDENCE DE LA SECTION
    // ---------------------------------------------------------

    function highlightSection(element) {
        document.querySelectorAll('.voice-guide-highlight')
            .forEach(function (el) {
                el.classList.remove('voice-guide-highlight');
            });

        if (!element) return;

        element.classList.add('voice-guide-highlight');

        /*
         * On évite de déplacer brutalement l'écran pour le hero.
         */
        if (!element.classList.contains('km-hero')) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }

    function removeHighlight() {
        document.querySelectorAll('.voice-guide-highlight')
            .forEach(function (el) {
                el.classList.remove('voice-guide-highlight');
            });
    }

    // ---------------------------------------------------------
    // CONTRÔLES
    // ---------------------------------------------------------

    function nomDeLaPageActuelle() {
        const h1 = document.querySelector('h1');
        if (h1 && cleanText(h1.innerText)) return cleanText(h1.innerText);
        if (document.title) return document.title.split('-')[0].trim();
        return 'cette page';
    }

    function startGuide() {
        if (!isSupported()) {
            alert(
                "La synthèse vocale n'est pas disponible sur ce navigateur."
            );
            return;
        }

        setEnabled(true);

        buildGuide();

        currentIndex = 0;
        isReadingGuide = true;

        const annonce = new SpeechSynthesisUtterance(
            'Vous êtes sur ' + nomDeLaPageActuelle() + '.'
        );
        const voix = getFrenchVoice();
        if (voix) annonce.voice = voix;
        annonce.lang = 'fr-FR';
        annonce.onend = function () {
            speakCurrentSection();
        };
        window.speechSynthesis.speak(annonce);
    }

    function pauseGuide() {
        if (!isSupported()) return;

        if (window.speechSynthesis.speaking &&
            !window.speechSynthesis.paused) {

            window.speechSynthesis.pause();
            updateButton('paused');
        }
    }

    function resumeGuide() {
        if (!isSupported()) return;

        if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
            updateButton('speaking');
        }
    }

    function stopGuide() {
        if (!isSupported()) return;

        isReadingGuide = false;
        window.speechSynthesis.cancel();

        removeHighlight();

        currentIndex = 0;

        updateButton('idle');
    }

    function finishGuide() {
        isReadingGuide = false;

        window.speechSynthesis.cancel();

        removeHighlight();

        currentIndex = 0;

        updateButton('idle');

        console.log('[VoiceGuide] Visite guidée terminée.');
    }

    function toggleGuide() {
        if (!isSupported()) return;

        /*
         * Si rien ne joue :
         * commencer la visite.
         */
        if (!window.speechSynthesis.speaking &&
            !window.speechSynthesis.paused) {

            startGuide();
            return;
        }

        /*
         * Si la lecture est en pause :
         * reprendre.
         */
        if (window.speechSynthesis.paused) {
            resumeGuide();
            return;
        }

        /*
         * Si la lecture est active :
         * mettre en pause.
         */
        pauseGuide();
    }

    // ---------------------------------------------------------
    // INITIALISATION
    // ---------------------------------------------------------

    function initWidget() {
        btn = document.getElementById('voiceBtn');
        icon = document.getElementById('voiceIcon');
        tooltip = document.getElementById('voiceTooltip');

        if (!btn) {
            console.warn('[VoiceGuide] Bouton #voiceBtn introuvable.');
            return;
        }

        if (!isSupported()) {
            btn.style.display = 'none';
            console.warn('[VoiceGuide] Synthèse vocale non disponible.');
            return;
        }

        updateButton('idle');

        btn.addEventListener('click', function () {
            toggleGuide();
        });

        /*
         * Double clic = arrêt complet.
         */
        btn.addEventListener('dblclick', function (event) {
            event.preventDefault();
            stopGuide();
        });

        /*
         * Charger les voix dès qu'elles deviennent disponibles.
         */
        window.speechSynthesis.addEventListener(
            'voiceschanged',
            function () {
                getFrenchVoice();
            }
        );

        window.addEventListener('beforeunload', function () {
            window.speechSynthesis.cancel();
        });

        console.log('[VoiceGuide] Guide vocal initialisé.');
    }

    // ---------------------------------------------------------
    // API PUBLIQUE
    // ---------------------------------------------------------

    window.VoiceGuide = {
        start: startGuide,
        stop: stopGuide,
        pause: pauseGuide,
        resume: resumeGuide,
        rebuild: buildGuide,
        isEnabled: isEnabled
    };

    /*
     * Le script est chargé avec "defer" dans base.html.
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }

})();