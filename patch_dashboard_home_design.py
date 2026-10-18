# -*- coding: utf-8 -*-
"""
Ameliore la mise en page du tableau de bord admin (dashboard/home.html) :
- graphiques a hauteur fixe (fin des zones vides demesurees sous les charts)
- empty states ("pas de donnees") centres au lieu de perdus en haut d'un
  grand bloc blanc
- colonnes Proprietaire/Zone qui affichent "None" remplacees par un tiret
Idempotent : si le patch est deja applique, le script le signale et ne
touche a rien. N'utilise que des ancres 100% ASCII (aucun accent) pour
eviter tout probleme d'encodage lors de la comparaison de texte.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) CSS : graphiques a hauteur fixe + centrage des empty states
# ---------------------------------------------------------------------
ANCRE_CSS = """    @media (prefers-reduced-motion: reduce) {
        .kpi-card, .panel, .recouvrement-bar-fill::after {
            animation: none !important;
            opacity: 1 !important;
            transform: none !important;
        }
    }
</style>
{% endblock %}"""
AJOUT_CSS = """    @media (prefers-reduced-motion: reduce) {
        .kpi-card, .panel, .recouvrement-bar-fill::after {
            animation: none !important;
            opacity: 1 !important;
            transform: none !important;
        }
    }

    /* ===== Redesign : graphiques a hauteur fixe + empty states harmonises ===== */
    .chart-wrap { position: relative; width: 100%; height: 300px; }
    .chart-wrap-sm { height: 220px; }
    .stats-charts-row .panel-body {
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 220px;
    }
    .stats-charts-row .panel-body p { margin: 0 auto; max-width: 320px; }
</style>
{% endblock %}"""
if "chart-wrap" in texte:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# 2) HTML : graphique "Evolution des paiements" a hauteur fixe
# ---------------------------------------------------------------------
ANCRE_EVO = '    <canvas id="chartEvolution" height="90"></canvas>\n'
AJOUT_EVO = '    <div class="chart-wrap"><canvas id="chartEvolution"></canvas></div>\n'
if '<div class="chart-wrap"><canvas id="chartEvolution">' in texte:
    pass
elif ANCRE_EVO not in texte:
    erreurs.append("ANCRE_EVO introuvable")
else:
    texte = texte.replace(ANCRE_EVO, AJOUT_EVO, 1)

# ---------------------------------------------------------------------
# 3) HTML : graphique "Taux de recouvrement par zone" a hauteur fixe
# ---------------------------------------------------------------------
ANCRE_ZONES = '        <canvas id="chartZones" height="220"></canvas>\n'
AJOUT_ZONES = '        <div class="chart-wrap chart-wrap-sm"><canvas id="chartZones"></canvas></div>\n'
if '<div class="chart-wrap chart-wrap-sm"><canvas id="chartZones">' in texte:
    pass
elif ANCRE_ZONES not in texte:
    erreurs.append("ANCRE_ZONES introuvable")
else:
    texte = texte.replace(ANCRE_ZONES, AJOUT_ZONES, 1)

# ---------------------------------------------------------------------
# 4) HTML : graphique "Repartition par type de taxe" a hauteur fixe
# ---------------------------------------------------------------------
ANCRE_TAXES = '        <canvas id="chartTaxes" height="220"></canvas>\n'
AJOUT_TAXES = '        <div class="chart-wrap chart-wrap-sm"><canvas id="chartTaxes"></canvas></div>\n'
if '<div class="chart-wrap chart-wrap-sm"><canvas id="chartTaxes">' in texte:
    pass
elif ANCRE_TAXES not in texte:
    erreurs.append("ANCRE_TAXES introuvable")
else:
    texte = texte.replace(ANCRE_TAXES, AJOUT_TAXES, 1)

# ---------------------------------------------------------------------
# 5) HTML : colonnes Proprietaire / Zone -> tiret au lieu de "None"
# ---------------------------------------------------------------------
ANCRE_TABLE = """          <td>{{ parcelle.nicad }}</td>
          <td>{{ parcelle.proprietaire }}</td>
          <td>{{ parcelle.zone }}</td>
          <td><span class="badge badge-danger">{{ parcelle.montant_taxe_annuelle|floatformat:0 }} FCFA</span></td>"""
AJOUT_TABLE = """          <td>{{ parcelle.nicad }}</td>
          <td>{% if parcelle.proprietaire and parcelle.proprietaire != "None" %}{{ parcelle.proprietaire }}{% else %}<span style="color:var(--ink-quiet, #7a7266);">&mdash;</span>{% endif %}</td>
          <td>{% if parcelle.zone and parcelle.zone != "None" %}{{ parcelle.zone }}{% else %}<span style="color:var(--ink-quiet, #7a7266);">&mdash;</span>{% endif %}</td>
          <td><span class="badge badge-danger">{{ parcelle.montant_taxe_annuelle|floatformat:0 }} FCFA</span></td>"""
if 'parcelle.proprietaire != "None"' in texte:
    pass
elif ANCRE_TABLE not in texte:
    erreurs.append("ANCRE_TABLE introuvable")
else:
    texte = texte.replace(ANCRE_TABLE, AJOUT_TABLE, 1)

# ---------------------------------------------------------------------
# 6) JS : maintainAspectRatio sur les 3 graphiques (pour respecter la
#    hauteur fixe des conteneurs ajoutes ci-dessus)
# ---------------------------------------------------------------------
ANCRE_JS_EVO = """            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: function (v) { return v.toLocaleString('fr-FR') + ' F'; } }
                    }
                }
            }"""
AJOUT_JS_EVO = """            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: function (v) { return v.toLocaleString('fr-FR') + ' F'; } }
                    }
                }
            }"""
if ANCRE_JS_EVO in texte:
    texte = texte.replace(ANCRE_JS_EVO, AJOUT_JS_EVO, 1)
# (si l'ancre n'est pas trouvee, c'est que ce bloc a deja ete patche lors
#  d'une execution precedente -- rien a faire, pas une erreur bloquante)

ANCRE_JS_ZONES = """            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, max: 100, ticks: { callback: function (v) { return v + '%'; } } } }
            }"""
AJOUT_JS_ZONES = """            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, max: 100, ticks: { callback: function (v) { return v + '%'; } } } }
            }"""
if ANCRE_JS_ZONES in texte:
    texte = texte.replace(ANCRE_JS_ZONES, AJOUT_JS_ZONES, 1)

ANCRE_JS_TAXES = """            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }"""
AJOUT_JS_TAXES = """            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }"""
if ANCRE_JS_TAXES in texte:
    texte = texte.replace(ANCRE_JS_TAXES, AJOUT_JS_TAXES, 1)

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
    print("OK : dashboard/home.html mis a jour (redesign tableau de bord).")