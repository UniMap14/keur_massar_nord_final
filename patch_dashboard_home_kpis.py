# -*- coding: utf-8 -*-
"""
Phase 2 du redesign du tableau de bord admin (dashboard/home.html) :
- 3 nouvelles cartes KPI (Contribuables enregistres, Demandes en cours,
  Infrastructures recensees) avec sparkline + variation % REELLES
  (donnees fournies par le patch backend patch_dashboard_views_kpis.py,
  qui doit etre applique AVANT celui-ci)
- une legende avec pourcentages a cote du donut "Repartition par type
  de taxe" (recalculee a partir des memes donnees que le graphique,
  aucune donnee inventee)
- le graphique "Evolution des paiements" passe de barres a une courbe
  en aire degradee (effet plus "moderne", memes donnees)

Pre-requis : foncier/templates/dashboard/home.html doit deja avoir recu
le patch patch_dashboard_home_design.py (hauteur fixe des graphiques).

Idempotent : si le patch est deja applique, le script le signale et ne
touche a rien. N'utilise que des ancres 100% ASCII pour eviter tout
probleme d'encodage.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

DEJA_APPLIQUE = "kpiSparkContribuables" in texte

# ---------------------------------------------------------------------
# 1) CSS : nouvelle teinte violette, badges de variation, legende donut
# ---------------------------------------------------------------------
ANCRE_CSS = """    .stats-charts-row .panel-body p { margin: 0 auto; max-width: 320px; }
</style>
{% endblock %}"""
AJOUT_CSS = """    .stats-charts-row .panel-body p { margin: 0 auto; max-width: 320px; }

    /* ===== Nouvelles cartes KPI + legende donut (phase 2) ===== */
    .kpi-card.tone-purple .kpi-icon { background: rgba(123,63,160,0.12); color: #7b3fa0; }
    .kpi-card.tone-purple { color: #7b3fa0; }

    .kpi-delta-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11.5px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 999px;
        margin-left: 8px;
    }
    .kpi-delta-badge i { font-size: 9px; }
    .kpi-delta-badge.up { background: rgba(58,125,68,0.12); color: #3a7d44; }
    .kpi-delta-badge.down { background: rgba(179,38,30,0.10); color: #b3261e; }
    .kpi-delta-row { margin-top: 6px; }

    .chart-legend-list { list-style: none; margin: 14px 0 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
    .chart-legend-list li { display: flex; align-items: center; gap: 10px; font-size: 12.5px; }
    .chart-legend-list .legend-swatch { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
    .chart-legend-list .legend-label { flex: 1; color: var(--ink, #2a2620); }
    .chart-legend-list .legend-pct { font-weight: 700; color: var(--ink-quiet, #7a7266); }
</style>
{% endblock %}"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# 2) HTML : badge de variation sur la carte Recouvrement (existante)
# ---------------------------------------------------------------------
ANCRE_RECOUV = '    <div class="kpi-sparkline-wrap"><canvas id="kpiSparkRecouvrement"></canvas></div>\n  </div>'
AJOUT_RECOUV = '''    <div class="kpi-sparkline-wrap"><canvas id="kpiSparkRecouvrement"></canvas></div>
    {% if delta_recouvrement is not None %}<div class="kpi-delta-row"><span class="kpi-delta-badge {% if delta_recouvrement >= 0 %}up{% else %}down{% endif %}"><i class="fa-solid fa-arrow-{% if delta_recouvrement >= 0 %}up{% else %}down{% endif %}"></i> {{ delta_recouvrement }}% vs mois precedent</span></div>{% endif %}
  </div>'''
if DEJA_APPLIQUE:
    pass
elif ANCRE_RECOUV not in texte:
    erreurs.append("ANCRE_RECOUV introuvable")
else:
    texte = texte.replace(ANCRE_RECOUV, AJOUT_RECOUV, 1)

# ---------------------------------------------------------------------
# 3) HTML : 3 nouvelles cartes KPI, inserees juste avant la carte
#    "Messages non traites" (derniere carte du kpi-grid)
# ---------------------------------------------------------------------
ANCRE_MESSAGES = '''  <a href="{% url 'dashboard_message_list' %}" class="kpi-card tone-gold" style="text-decoration:none; color:inherit; display:block;">'''
AJOUT_MESSAGES = '''{% if peut_fiscal %}
  <a href="{% url 'dashboard_contribuable_list' %}" class="kpi-card tone-purple" style="text-decoration:none; color:inherit; display:block;">
    <div class="kpi-icon"><i class="fa-solid fa-id-card"></i></div>
    <div class="label">Contribuables enregistres</div>
    <div class="value">{{ nb_contribuables }}</div>
    <div class="delta">Inscrits au role fiscal</div>
    {% if delta_contribuables is not None %}<div class="kpi-delta-row"><span class="kpi-delta-badge {% if delta_contribuables >= 0 %}up{% else %}down{% endif %}"><i class="fa-solid fa-arrow-{% if delta_contribuables >= 0 %}up{% else %}down{% endif %}"></i> {{ delta_contribuables }}%</span></div>{% endif %}
    <div class="kpi-sparkline-wrap"><canvas id="kpiSparkContribuables"></canvas></div>
  </a>

{% endif %}
  <a href="{% url 'dashboard_demande_list' %}" class="kpi-card tone-gold" style="text-decoration:none; color:inherit; display:block;">
    <div class="kpi-icon"><i class="fa-solid fa-folder-open"></i></div>
    <div class="label">Demandes en cours</div>
    <div class="value">{{ nb_demandes_en_cours }}</div>
    <div class="delta">Dossiers a traiter</div>
    {% if delta_demandes is not None %}<div class="kpi-delta-row"><span class="kpi-delta-badge {% if delta_demandes >= 0 %}up{% else %}down{% endif %}"><i class="fa-solid fa-arrow-{% if delta_demandes >= 0 %}up{% else %}down{% endif %}"></i> {{ delta_demandes }}%</span></div>{% endif %}
    <div class="kpi-sparkline-wrap"><canvas id="kpiSparkDemandes"></canvas></div>
  </a>

{% if peut_technique %}
  <div class="kpi-card tone-blue">
    <div class="kpi-icon"><i class="fa-solid fa-road-bridge"></i></div>
    <div class="label">Infrastructures recensees</div>
    <div class="value">{{ nb_infrastructures }}</div>
    <div class="delta">Equipements suivis</div>
    {% if delta_infra is not None %}<div class="kpi-delta-row"><span class="kpi-delta-badge {% if delta_infra >= 0 %}up{% else %}down{% endif %}"><i class="fa-solid fa-arrow-{% if delta_infra >= 0 %}up{% else %}down{% endif %}"></i> {{ delta_infra }}%</span></div>{% endif %}
    <div class="kpi-sparkline-wrap"><canvas id="kpiSparkInfra"></canvas></div>
  </div>

{% endif %}
  <a href="{% url 'dashboard_message_list' %}" class="kpi-card tone-gold" style="text-decoration:none; color:inherit; display:block;">'''
if DEJA_APPLIQUE:
    pass
elif ANCRE_MESSAGES not in texte:
    erreurs.append("ANCRE_MESSAGES introuvable")
else:
    texte = texte.replace(ANCRE_MESSAGES, AJOUT_MESSAGES, 1)

# ---------------------------------------------------------------------
# 4) HTML : legende (liste + pourcentages) a cote du donut des taxes
# ---------------------------------------------------------------------
ANCRE_DONUT = '<div class="chart-wrap chart-wrap-sm"><canvas id="chartTaxes"></canvas></div>'
AJOUT_DONUT = '<div class="chart-wrap chart-wrap-sm"><canvas id="chartTaxes"></canvas></div>\n      <ul id="legendeTaxes" class="chart-legend-list"></ul>'
if 'id="legendeTaxes"' in texte:
    pass
elif ANCRE_DONUT not in texte:
    erreurs.append("ANCRE_DONUT introuvable")
else:
    texte = texte.replace(ANCRE_DONUT, AJOUT_DONUT, 1)

# ---------------------------------------------------------------------
# 5) JS : graphique "Evolution des paiements" -> courbe en aire degradee
#    (on ne touche jamais au texte du label du dataset, qui contient un
#    accent, uniquement au type de graphique et au style du dataset)
# ---------------------------------------------------------------------
ANCRE_JS_TYPE = """    var elEvolution = document.getElementById('chartEvolution');
    if (elEvolution) {
        new Chart(elEvolution, {
            type: 'bar',"""
AJOUT_JS_TYPE = """    var elEvolution = document.getElementById('chartEvolution');
    if (elEvolution) {
        new Chart(elEvolution, {
            type: 'line',"""
if "pointBackgroundColor: '#c9982e'" in texte:
    pass  # deja applique lors d'une execution precedente
elif ANCRE_JS_TYPE not in texte:
    erreurs.append("ANCRE_JS_TYPE introuvable")
else:
    texte = texte.replace(ANCRE_JS_TYPE, AJOUT_JS_TYPE, 1)

ANCRE_JS_STYLE = """                    backgroundColor: 'rgba(47,122,79,0.75)',
                    borderRadius: 5,
                    maxBarThickness: 34,"""
AJOUT_JS_STYLE = """                    borderColor: '#c9982e',
                    backgroundColor: 'rgba(201,152,46,0.18)',
                    fill: true,
                    tension: 0.35,
                    pointRadius: 3,
                    pointBackgroundColor: '#c9982e',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,"""
if "pointBackgroundColor: '#c9982e'" in texte:
    pass  # deja applique (soit a l'instant par le bloc ci-dessus, soit avant)
elif ANCRE_JS_STYLE not in texte:
    erreurs.append("ANCRE_JS_STYLE introuvable")
else:
    texte = texte.replace(ANCRE_JS_STYLE, AJOUT_JS_STYLE, 1)

# ---------------------------------------------------------------------
# 6) JS : 3 nouvelles sparklines + legende du donut (calculee cote
#    client a partir des memes tableaux deja utilises par le graphique)
# ---------------------------------------------------------------------
ANCRE_JS_TAXES = "    var elTaxes = document.getElementById('chartTaxes');\n"
AJOUT_JS_TAXES = '''    var elSparkContribuables = document.getElementById('kpiSparkContribuables');
    if (elSparkContribuables) {
        new Chart(elSparkContribuables, {
            type: 'line',
            data: {
                labels: {{ chart_mois_labels|safe }},
                datasets: [{
                    data: {{ chart_contribuables_valeurs|safe }},
                    borderColor: '#7b3fa0',
                    backgroundColor: 'rgba(123,63,160,0.12)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.35,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } },
            }
        });
    }

    var elSparkDemandes = document.getElementById('kpiSparkDemandes');
    if (elSparkDemandes) {
        new Chart(elSparkDemandes, {
            type: 'line',
            data: {
                labels: {{ chart_mois_labels|safe }},
                datasets: [{
                    data: {{ chart_demandes_valeurs|safe }},
                    borderColor: '#a3791f',
                    backgroundColor: 'rgba(201,152,46,0.12)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.35,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } },
            }
        });
    }

    var elSparkInfra = document.getElementById('kpiSparkInfra');
    if (elSparkInfra) {
        new Chart(elSparkInfra, {
            type: 'line',
            data: {
                labels: {{ chart_mois_labels|safe }},
                datasets: [{
                    data: {{ chart_infra_valeurs|safe }},
                    borderColor: '#2d64a0',
                    backgroundColor: 'rgba(45,100,160,0.12)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.35,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } },
            }
        });
    }

    var elTaxes = document.getElementById('chartTaxes');
'''
if "elSparkContribuables" in texte:
    pass
elif ANCRE_JS_TAXES not in texte:
    erreurs.append("ANCRE_JS_TAXES introuvable")
else:
    texte = texte.replace(ANCRE_JS_TAXES, AJOUT_JS_TAXES, 1)

ANCRE_JS_LEGENDE = "    var elTaxes = document.getElementById('chartTaxes');\n    if (elTaxes) {\n"
AJOUT_JS_LEGENDE = '''    var elTaxes = document.getElementById('chartTaxes');
    if (elTaxes) {
        var elLegendeTaxes = document.getElementById('legendeTaxes');
        if (elLegendeTaxes) {
            var labelsTaxesLegende = {{ chart_taxes_labels|safe }};
            var valeursTaxesLegende = {{ chart_taxes_valeurs|safe }};
            var totalTaxesLegende = valeursTaxesLegende.reduce(function (a, b) { return a + b; }, 0);
            elLegendeTaxes.innerHTML = labelsTaxesLegende.map(function (label, i) {
                var pct = totalTaxesLegende > 0 ? Math.round((valeursTaxesLegende[i] / totalTaxesLegende) * 100) : 0;
                var couleur = palette[i % palette.length];
                return '<li><span class="legend-swatch" style="background:' + couleur + ';"></span>' +
                       '<span class="legend-label">' + label + '</span>' +
                       '<span class="legend-pct">' + pct + '%</span></li>';
            }).join('');
        }
'''
if "elLegendeTaxes" in texte and "elLegendeTaxes.innerHTML" in texte:
    pass
elif ANCRE_JS_LEGENDE not in texte:
    erreurs.append("ANCRE_JS_LEGENDE introuvable")
else:
    texte = texte.replace(ANCRE_JS_LEGENDE, AJOUT_JS_LEGENDE, 1)

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
    print("OK : dashboard/home.html mis a jour (phase 2 : nouvelles cartes KPI + legende + courbe).")