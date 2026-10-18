# -*- coding: utf-8 -*-
"""
Round 8 (sur home.html) :
1) "Taux de recouvrement" : remplace la barre de progression horizontale
   par un donut Chart.js avec le pourcentage reel centre (meme donnee
   reelle taux_recouvrement, seul le style visuel change, pour se
   rapprocher de la maquette).
2) Attenue le fond quadrille decoratif (geo-access-card et
   quick-actions-banner) -- opacite et pas de grille reduits, pour un
   rendu plus epure comme demande dans le cahier des charges.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1a) HTML : barre -> donut + pourcentage centre
# ---------------------------------------------------------------------
ANCRE_HTML = """  <div class="panel-body">
    <div class="recouvrement-bar-track">
      <div class="recouvrement-bar-fill" data-target="{{ taux_recouvrement }}" style="
        background: {% if taux_recouvrement >= 75 %}#3a7d44{% elif taux_recouvrement >= 40 %}#c9982e{% else %}#b3261e{% endif %};
      "></div>
    </div>"""
AJOUT_HTML = """  <div class="panel-body">
    <div class="recouvrement-donut-wrap">
      <canvas id="chartRecouvrementDonut"></canvas>
      <div class="recouvrement-donut-center">
        <span class="recouvrement-donut-pct">{{ taux_recouvrement }}%</span>
      </div>
    </div>"""
if "recouvrement-donut-wrap" in texte:
    pass
elif ANCRE_HTML not in texte:
    erreurs.append("ANCRE_HTML (donut) introuvable")
else:
    texte = texte.replace(ANCRE_HTML, AJOUT_HTML, 1)

# ---------------------------------------------------------------------
# 1b) CSS : styles du donut + attenuation des 2 fonds quadrilles
# ---------------------------------------------------------------------
ANCRE_CSS = """    .dashboard-grid .quick-action-tile span { font-size: 9px !important; line-height: 1.2 !important; }
</style>
{% endblock %}"""
AJOUT_CSS = """    .dashboard-grid .quick-action-tile span { font-size: 9px !important; line-height: 1.2 !important; }

    /* ===== Donut "Taux de recouvrement" (round 8) ===== */
    .recouvrement-donut-wrap {
        position: relative;
        width: 100px;
        height: 100px;
        margin: 2px auto 0;
    }
    .recouvrement-donut-center {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
    }
    .recouvrement-donut-pct {
        font-size: 17px;
        font-weight: 800;
        color: var(--ink, #2a2620);
    }

    /* ===== Fond quadrille attenue (round 8) ===== */
    .geo-access-card::before,
    .quick-actions-banner::before {
        background-size: 42px 42px !important;
        opacity: 0.45 !important;
    }
</style>
{% endblock %}"""
if "Donut \"Taux de recouvrement\" (round 8)" in texte:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# 1c) JS : Chart.js doughnut pour le nouveau canvas
# ---------------------------------------------------------------------
ANCRE_JS = """    var elEvolution = document.getElementById('chartEvolution');"""
AJOUT_JS = """    var elRecouvrementDonut = document.getElementById('chartRecouvrementDonut');
    if (elRecouvrementDonut) {
        var tauxRecouvrement = {{ taux_recouvrement|default:0 }};
        var couleurRecouvrement = tauxRecouvrement >= 75 ? '#3a7d44' : (tauxRecouvrement >= 40 ? '#c9982e' : '#b3261e');
        new Chart(elRecouvrementDonut, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [tauxRecouvrement, Math.max(0, 100 - tauxRecouvrement)],
                    backgroundColor: [couleurRecouvrement, '#eee6d6'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
            }
        });
    }

    var elEvolution = document.getElementById('chartEvolution');"""
if "chartRecouvrementDonut" in texte and "new Chart(elRecouvrementDonut" in texte:
    pass
elif ANCRE_JS not in texte:
    erreurs.append("ANCRE_JS introuvable")
else:
    texte = texte.replace(ANCRE_JS, AJOUT_JS, 1)

# ---------------------------------------------------------------------
if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard/home.html -- round 8 (donut recouvrement + fond quadrille attenue).")