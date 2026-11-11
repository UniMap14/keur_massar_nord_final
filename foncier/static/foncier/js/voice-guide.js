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

    function limitText(text, maxLength) {
        const cleaned = cleanText(text);
        if (cleaned.length <= maxLength) return cleaned;

        const excerpt = cleaned.slice(0, maxLength);
        const lastSpace = excerpt.lastIndexOf(' ');
        return excerpt.slice(0, lastSpace > 0 ? lastSpace : maxLength).trim() + '…';
    }

    function summarizeElement(element) {
        if (!element) return '';

        const statItems = element.querySelectorAll('.km-page2-stat');
        if (statItems.length) {
            return Array.from(statItems).map(function (item) {
                const value = item.querySelector('strong');
                const label = item.querySelector('span');
                return cleanText((value ? value.innerText : '') + ' ' + (label ? label.innerText : ''));
            }).filter(Boolean).join(', ');
        }

        const serviceNames = element.querySelectorAll('.km-bento-small h4');
        if (serviceNames.length) {
            return 'Les services proposés comprennent : ' +
                Array.from(serviceNames).slice(0, 6)
                    .map(function (heading) { return cleanText(heading.innerText); })
                    .filter(Boolean)
                    .join(', ') + '.';
        }

        const heading = element.querySelector('h1, h2, h3');
        const paragraph = element.querySelector('p');
        const parts = [];

        if (heading) parts.push(cleanText(heading.innerText));
        if (paragraph) {
            const paragraphText = cleanText(paragraph.innerText);
            if (paragraphText && paragraphText !== parts[0]) parts.push(paragraphText);
        }

        return limitText(parts.join('. '), 280);
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
         * Guides courts par page. On ne lit pas le contenu complet des
         * grands blocs : chaque étape ne garde que son résumé utile.
         */
        const cheminActuel = window.location.pathname;

        const jeuxDeSelecteurs = {
            accueil: [
                {
                    selector: '.km-hero',
                    text: 'Dalal ak jàmm ci Keur Massar Nord.',
                    language: 'wo-SN'
                },
                {
                    selector: '.km-page2-stats-bar',
                    intro: 'Bienvenue sur le portail officiel de Keur Massar Nord. Découvrez la commune en quelques chiffres.'
                },
                {
                    selector: '.km-page2-maire-text',
                    text: 'Le mot du maire présente les ambitions de modernisation de la commune et l’engagement pour une gestion foncière et fiscale plus transparente.'
                },
                {
                    selector: '.km-bento-intro',
                    text: 'Depuis la page d’accueil, accédez aux démarches en ligne, aux informations foncières et fiscales, aux actualités, aux statistiques et au signalement citoyen.'
                },
                {
                    selector: '.km-bento-grid-small',
                    intro: 'Les principaux services disponibles.'
                },
                {
                    selector: '.main-section',
                    intro: 'À propos de la commune.'
                },
                {
                    selector: '.security-section',
                    intro: 'La plateforme met l’accent sur la confiance et la protection des données.'
                }
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
            selectors = [];
            const pageSections = document.querySelectorAll('main section, .main-content section, section');
            pageSections.forEach(function (section) {
                if (!section.parentElement.closest('section')) {
                    selectors.push({ element: section, intro: '' });
                }
            });
            if (!selectors.length && document.querySelector('h1')) {
                selectors.push({ element: document.querySelector('h1'), intro: '' });
            }
        }

        const textesDejaAjoutes = new Set();
        selectors.forEach(function (item) {
            const element = item.element || document.querySelector(item.selector);

            if (!element) return;

            const texteResume = item.text || summarizeElement(element);
            const text = limitText([item.intro, texteResume].filter(Boolean).join(' '), 320);

            if (!text || textesDejaAjoutes.has(text)) return;
            textesDejaAjoutes.add(text);

            sections.push({
                element: element,
                text: text,
                language: item.language || 'fr-FR'
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

        utterance.lang = section.language;
        utterance.rate = 0.95;
        utterance.pitch = 1;

        const voices = window.speechSynthesis.getVoices();
        const voice = section.language.toLowerCase().startsWith('wo')
            ? voices.find(function (candidate) {
                return candidate.lang && candidate.lang.toLowerCase().startsWith('wo');
            }) || getFrenchVoice()
            : getFrenchVoice();

        if (voice) {
            utterance.voice = voice;
            if (section.language.toLowerCase().startsWith('wo') &&
                (!voice.lang || !voice.lang.toLowerCase().startsWith('wo'))) {
                utterance.lang = voice.lang;
            }
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

        if (window.location.pathname === '/' ||
            window.location.pathname.indexOf('/accueil') !== -1) {
            speakCurrentSection();
            return;
        }

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