# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien_js = '''document.addEventListener('DOMContentLoaded', function () {
    // Verrouille le defilement tant que l'utilisateur n'a pas clique sur
    // "Decouvrir la commune" : impossible d'atteindre les sections en dessous
    // du Hero sans passer par ce bouton.
    var hero = document.getElementById('hero');'''

nouveau_js = '''document.addEventListener('DOMContentLoaded', function () {
    // ===== Compteurs animes "Keur Massar en chiffres" =====
    function animerCompteurs() {
        document.querySelectorAll('.km-page2-stat strong[data-cible]').forEach(function (el) {
            var cibleTexte = el.getAttribute('data-cible');
            var estDecimal = cibleTexte.indexOf(',') !== -1;
            var cibleNombre = parseFloat(cibleTexte.replace(/\\s/g, '').replace(',', '.'));
            if (isNaN(cibleNombre)) return;

            el.textContent = estDecimal ? '0,00' : '0';
            var debut = null;
            var duree = 1600;

            function etape(horodatage) {
                if (!debut) debut = horodatage;
                var progres = Math.min((horodatage - debut) / duree, 1);
                var valeurActuelle = cibleNombre * progres;
                el.textContent = estDecimal
                    ? valeurActuelle.toFixed(2).replace('.', ',')
                    : Math.round(valeurActuelle).toLocaleString('fr-FR');
                if (progres < 1) {
                    requestAnimationFrame(etape);
                } else {
                    el.textContent = cibleTexte;
                }
            }
            requestAnimationFrame(etape);
        });
    }

    if ('IntersectionObserver' in window) {
        var page2El = document.getElementById('page-chiffres');
        if (page2El) {
            var observateurChiffres = new IntersectionObserver(function (entrees) {
                entrees.forEach(function (entree) {
                    if (entree.isIntersecting) {
                        animerCompteurs();
                    }
                });
            }, { threshold: 0.4 });
            observateurChiffres.observe(page2El);
        }
    }

    // Verrouille le defilement tant que l'utilisateur n'a pas clique sur
    // "Decouvrir la commune" : impossible d'atteindre les sections en dessous
    // du Hero sans passer par ce bouton.
    var hero = document.getElementById('hero');'''

if "function animerCompteurs" in contenu:
    print("IGNORE : JS compteurs deja present.")
elif ancien_js in contenu:
    contenu = contenu.replace(ancien_js, nouveau_js, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : JS du compteur anime ajoute.")
else:
    print("ERREUR : point d'ancrage toujours introuvable.")