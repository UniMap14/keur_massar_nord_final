CHEMIN = "foncier/static/foncier/js/voice-guide.js"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    function startGuide() {
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

        speakCurrentSection();
    }'''

nouveau = '''    function nomDeLaPageActuelle() {
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
    }'''

if "nomDeLaPageActuelle" in contenu:
    print("IGNORE : annonce de page deja presente.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : annonce 'Vous etes sur...' ajoutee au demarrage du guide.")
else:
    print("ERREUR : fonction startGuide() introuvable telle quelle.")