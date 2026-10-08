# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. HTML : ajout de data-cible sur chaque <strong> de stat
# ============================================================
remplacements_html = [
    ('<strong>{{ population|default:"224 765" }}</strong>',
     '<strong data-cible="{{ population|default:\'224 765\' }}">{{ population|default:"224 765" }}</strong>'),
    ('<strong>{{ nb_quartiers|default:"86" }}</strong>',
     '<strong data-cible="{{ nb_quartiers|default:\'86\' }}">{{ nb_quartiers|default:"86" }}</strong>'),
    ('<strong>{{ annee_creation|default:"2021" }}</strong>',
     '<strong data-cible="{{ annee_creation|default:\'2021\' }}">{{ annee_creation|default:"2021" }}</strong>'),
    ('<strong>{{ superficie|default:"13,18" }}</strong>',
     '<strong data-cible="{{ superficie|default:\'13,18\' }}">{{ superficie|default:"13,18" }}</strong>'),
]

for ancien, nouveau in remplacements_html:
    if 'data-cible' in contenu and nouveau in contenu:
        resultats.append(f"HTML (deja fait) : {ancien[:40]}...")
    elif ancien in contenu:
        contenu = contenu.replace(ancien, nouveau, 1)
        resultats.append(f"HTML OK : {ancien[:40]}...")
    else:
        resultats.append(f"HTML ERREUR introuvable : {ancien[:40]}...")

# ============================================================
# 2. JS : animation de comptage, rejouee a chaque apparition
#    de la Page 2 dans la fenetre visible
# ============================================================
ancien_js = '''<script>
document.addEventListener('DOMContentLoaded', function () {
    var hero = document.getElementById('hero');
    var btnDecouvrir = document.getElementById('btnDecouvrir');'''

nouveau_js = '''<script>
document.addEventListener('DOMContentLoaded', function () {
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

    var hero = document.getElementById('hero');
    var btnDecouvrir = document.getElementById('btnDecouvrir');'''

if "function animerCompteurs" in contenu:
    resultats.append("JS compteurs : IGNORE (deja present)")
elif ancien_js in contenu:
    contenu = contenu.replace(ancien_js, nouveau_js, 1)
    resultats.append("JS compteurs : OK (animation ajoutee)")
else:
    resultats.append("JS compteurs : ERREUR point d'ancrage introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))