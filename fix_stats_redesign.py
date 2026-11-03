# -*- coding: utf-8 -*-
import io

# ============================================================
# 1) foncier/views.py : simplifier statistiques() (on retire
#    la repartition "occupation du sol", plus affichee).
# ============================================================
chemin_views = "foncier/views.py"
with io.open(chemin_views, "r", encoding="utf-8") as f:
    contenu_views = f.read()

ancienne_fonction = """def statistiques(request):
    import json

    context = {
        'population': "224 765",        # RGPH-5 (2023), ANSD
        'annee_population': 2023,
        'superficie': "13,18",
        'densite': "17 058",
        'pop_hommes_pct': "50,7",
        'pop_femmes_pct': "49,3",
        'nb_quartiers': 86,
        'annee_creation': 2021,
    }

    # Valeurs numériques utilisées par les graphiques (les chaînes
    # ci-dessus, avec virgule, restent pour l'affichage textuel).
    context['chart_population_labels'] = json.dumps(['Hommes', 'Femmes'])
    context['chart_population_valeurs'] = json.dumps([50.7, 49.3])

    # --- Données cadastrales réelles (calculées à partir des parcelles
    # effectivement importées en base, pas de chiffres inventés) ---
    nb_parcelles = Parcelle.objects.count()
    context['nb_parcelles'] = nb_parcelles

    if nb_parcelles:
        superficie_totale_m2 = (
            Parcelle.objects.aggregate(total=Sum('superficie'))['total'] or 0
        )
        context['superficie_cadastree_ha'] = round(superficie_totale_m2 / 10000, 1)

        # Répartition par occupation du sol (les 6 catégories les plus
        # fréquentes, pour ne pas afficher une liste trop longue).
        repartition = (
            Parcelle.objects
            .exclude(occupation_sol='')
            .values('occupation_sol')
            .annotate(total=Count('id'))
            .order_by('-total')[:6]
        )
        max_total = repartition[0]['total'] if repartition else 1
        context['repartition_occupation'] = [
            {
                'label': r['occupation_sol'],
                'total': r['total'],
                'pourcentage': round(100 * r['total'] / nb_parcelles, 1),
                'largeur_barre': round(100 * r['total'] / max_total, 1),
            }
            for r in repartition
        ]
        context['chart_occupation_labels'] = json.dumps(
            [r['occupation_sol'] for r in repartition]
        )
        context['chart_occupation_valeurs'] = json.dumps(
            [r['total'] for r in repartition]
        )

        # Nombre de parcelles par quartier (top 15, pour rester lisible
        # sur un graphique).
        parcelles_par_quartier = list(
            Parcelle.objects
            .exclude(zone__isnull=True)
            .values('zone__nom')
            .annotate(total=Count('id'))
            .order_by('-total')[:15]
        )
        context['parcelles_par_quartier'] = parcelles_par_quartier
        context['chart_quartiers_labels'] = json.dumps(
            [q['zone__nom'] for q in parcelles_par_quartier]
        )
        context['chart_quartiers_valeurs'] = json.dumps(
            [q['total'] for q in parcelles_par_quartier]
        )

    # --- Infrastructures publiques réellement recensées ---
    context['nb_infrastructures'] = Infrastructure.objects.count()
    repartition_infrastructures = list(
        CategorieInfrastructure.objects
        .annotate(total=Count('infrastructures'))
        .filter(total__gt=0)
        .order_by('-total')
    )
    context['repartition_infrastructures'] = repartition_infrastructures
    context['chart_infra_labels'] = json.dumps(
        [c.label for c in repartition_infrastructures]
    )
    context['chart_infra_valeurs'] = json.dumps(
        [c.total for c in repartition_infrastructures]
    )
    context['chart_infra_couleurs'] = json.dumps(
        [getattr(c, 'couleur', None) or '#2f7a4f' for c in repartition_infrastructures]
    )

    return render(request, 'foncier/statistiques.html', context)
"""

nouvelle_fonction = """def statistiques(request):
    import json

    context = {
        'population': "224 765",        # RGPH-5 (2023), ANSD
        'annee_population': 2023,
        'superficie': "13,18",
        'densite': "17 058",
        'pop_hommes_pct': "50,7",
        'pop_femmes_pct': "49,3",
        'nb_quartiers': 86,
        'annee_creation': 2021,
    }

    # Valeurs numériques utilisées par les graphiques (les chaînes
    # ci-dessus, avec virgule, restent pour l'affichage textuel).
    context['chart_population_labels'] = json.dumps(['Hommes', 'Femmes'])
    context['chart_population_valeurs'] = json.dumps([50.7, 49.3])

    # --- Données cadastrales réelles (calculées à partir des parcelles
    # effectivement importées en base, pas de chiffres inventés) ---
    nb_parcelles = Parcelle.objects.count()
    context['nb_parcelles'] = nb_parcelles

    if nb_parcelles:
        superficie_totale_m2 = (
            Parcelle.objects.aggregate(total=Sum('superficie'))['total'] or 0
        )
        context['superficie_cadastree_ha'] = round(superficie_totale_m2 / 10000, 1)

        # Nombre de parcelles par quartier (top 15, pour rester lisible
        # sur un graphique).
        parcelles_par_quartier = list(
            Parcelle.objects
            .exclude(zone__isnull=True)
            .values('zone__nom')
            .annotate(total=Count('id'))
            .order_by('-total')[:15]
        )
        context['parcelles_par_quartier'] = parcelles_par_quartier
        context['chart_quartiers_labels'] = json.dumps(
            [q['zone__nom'] for q in parcelles_par_quartier]
        )
        context['chart_quartiers_valeurs'] = json.dumps(
            [q['total'] for q in parcelles_par_quartier]
        )

    # --- Infrastructures publiques réellement recensées ---
    context['nb_infrastructures'] = Infrastructure.objects.count()
    repartition_infrastructures = list(
        CategorieInfrastructure.objects
        .annotate(total=Count('infrastructures'))
        .filter(total__gt=0)
        .order_by('-total')
    )
    context['repartition_infrastructures'] = repartition_infrastructures
    context['chart_infra_labels'] = json.dumps(
        [c.label for c in repartition_infrastructures]
    )
    context['chart_infra_valeurs'] = json.dumps(
        [c.total for c in repartition_infrastructures]
    )
    context['chart_infra_couleurs'] = json.dumps(
        [getattr(c, 'couleur', None) or '#2f7a4f' for c in repartition_infrastructures]
    )

    return render(request, 'foncier/statistiques.html', context)
"""

nb = contenu_views.count(ancienne_fonction)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre de statistiques() trouvee {nb} fois (attendu 1) dans views.py. "
        f"Rien n'a ete modifie."
    )
contenu_views = contenu_views.replace(ancienne_fonction, nouvelle_fonction)

with io.open(chemin_views, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_views)

# ============================================================
# 2) foncier/templates/foncier/statistiques.html : reecriture
#    complete (design epure, graphiques interactifs).
# ============================================================
nouveau_html = '''{% extends 'foncier/base.html' %}
{% load static %}
{% block title %}Statistiques - Keur Massar Nord{% endblock %}

{% block extra_head %}
<style>
  .stats-kpi-row{
    display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr));
    gap:18px; margin-top:36px;
  }
  .stats-kpi{
    background:#fff; border:1px solid var(--border); border-radius:var(--radius);
    padding:26px 18px; text-align:center;
    opacity:0; transform:translateY(10px); animation:statFadeIn .5s ease forwards;
    transition:transform .25s ease, box-shadow .25s ease;
  }
  .stats-kpi:hover{ transform:translateY(-4px); box-shadow:var(--shadow-md, 0 6px 18px rgba(0,0,0,.07)); }
  .stats-kpi:nth-child(1){ animation-delay:.03s; }
  .stats-kpi:nth-child(2){ animation-delay:.08s; }
  .stats-kpi:nth-child(3){ animation-delay:.13s; }
  .stats-kpi:nth-child(4){ animation-delay:.18s; }
  .stats-kpi:nth-child(5){ animation-delay:.23s; }
  .stats-kpi:nth-child(6){ animation-delay:.28s; }
  .stats-kpi:nth-child(7){ animation-delay:.33s; }
  .stats-kpi:nth-child(8){ animation-delay:.38s; }
  @keyframes statFadeIn{ to{ opacity:1; transform:translateY(0); } }

  .stats-kpi strong{
    display:block; font-family:'Playfair Display', serif; font-size:32px;
    color:var(--green-dark); line-height:1.15;
  }
  .stats-kpi span{
    font-size:12px; color:var(--text-muted); text-transform:uppercase;
    letter-spacing:.5px; display:block; margin-top:6px;
  }

  .stat-source-note{
    display:flex; align-items:center; gap:10px;
    margin-top:24px; padding:14px 18px;
    background:color-mix(in srgb, var(--green-dark) 6%, transparent);
    border:1px solid var(--border); border-radius:var(--radius);
    font-size:13px; color:var(--text-muted);
  }
  .stat-source-note i{ color:var(--green-dark); font-size:15px; flex-shrink:0; }

  .stats-section{ margin-top:60px; }
  .stats-section-head{
    display:flex; align-items:flex-end; justify-content:space-between;
    flex-wrap:wrap; gap:14px; margin-bottom:22px;
  }
  .stats-section-head h2{
    font-family:'Playfair Display', serif; font-size:23px; margin:0; color:#2c2620;
  }
  .stats-section-head p{ margin:4px 0 0; font-size:13.5px; color:var(--text-muted); }

  .chart-toggle{
    display:inline-flex; background:#f3f1ec; border-radius:999px; padding:4px; gap:2px;
  }
  .chart-toggle button{
    border:none; background:transparent; padding:8px 16px; border-radius:999px;
    font-size:12.5px; font-weight:600; color:var(--text-muted); cursor:pointer;
    transition:background .2s ease, color .2s ease; white-space:nowrap;
  }
  .chart-toggle button.active{ background:var(--green-dark); color:#fff; }
  .chart-toggle button:hover:not(.active){ background:rgba(0,0,0,0.05); }

  .chart-card{
    background:#fff; border:1px solid var(--border); border-radius:var(--radius);
    padding:32px; box-shadow:0 4px 22px rgba(0,0,0,.05);
  }
  .chart-card canvas{ max-height:420px; }

  .stats-two-col{ display:grid; grid-template-columns:1.3fr 1fr; gap:28px; align-items:center; }
  .stats-legend-list{ display:flex; flex-direction:column; gap:14px; }
  .stats-legend-item{ display:flex; align-items:center; gap:12px; font-size:14px; }
  .stats-legend-dot{ width:12px; height:12px; border-radius:50%; flex-shrink:0; }
  .stats-legend-item strong{ margin-left:auto; color:var(--green-dark); font-size:16px; }

  @media (max-width: 1000px){ .stats-two-col{ grid-template-columns:1fr; } }
  @media (max-width: 640px){ .chart-card{ padding:20px; } }
</style>
{% endblock %}

{% block content %}
<section class="main-section">
  <span class="section-label">Statistiques</span>
  <h2 class="section-title">Les chiffres clés de la commune</h2>
  <p class="section-sub">Aperçu démographique, territorial et cadastral de Keur Massar Nord.</p>

  <div class="stats-kpi-row">
    <div class="stats-kpi">
      <strong>{{ population|default:"224 765" }}</strong>
      <span>Population{% if annee_population %} (est. {{ annee_population }}){% endif %}</span>
    </div>
    <div class="stats-kpi">
      <strong>{{ superficie|default:"13,18" }} km&sup2;</strong>
      <span>Superficie</span>
    </div>
    <div class="stats-kpi">
      <strong>{{ densite|default:"17 058" }}</strong>
      <span>Habitants / km&sup2;</span>
    </div>
    <div class="stats-kpi">
      <strong>{{ nb_quartiers|default:"104" }}</strong>
      <span>Quartiers &amp; villages</span>
    </div>
    <div class="stats-kpi">
      <strong>{{ annee_creation|default:"2021" }}</strong>
      <span>Création de la commune</span>
    </div>
    {% if nb_parcelles %}
    <div class="stats-kpi">
      <strong>{{ nb_parcelles|floatformat:0 }}</strong>
      <span>Parcelles cadastrées</span>
    </div>
    {% endif %}
    {% if superficie_cadastree_ha %}
    <div class="stats-kpi">
      <strong>{{ superficie_cadastree_ha|floatformat:0 }} ha</strong>
      <span>Superficie cadastrée</span>
    </div>
    {% endif %}
    {% if nb_infrastructures %}
    <div class="stats-kpi">
      <strong>{{ nb_infrastructures|floatformat:0 }}</strong>
      <span>Infrastructures</span>
    </div>
    {% endif %}
  </div>

  <div class="stat-source-note">
    <i class="fa-solid fa-circle-info" aria-hidden="true"></i>
    <span>Données de population : RGPH-5 (2023), ANSD{% if annee_population %} — {{ annee_population }}{% endif %}. Pour des chiffres officiels, contactez la mairie de Keur Massar Nord.</span>
  </div>

  <div class="stats-section">
    <div class="stats-section-head">
      <div>
        <h2>Répartition de la population</h2>
        <p>Hommes et femmes{% if annee_population %}, estimation {{ annee_population }}{% endif %}</p>
      </div>
    </div>
    <div class="stats-two-col">
      <div class="chart-card">
        <canvas id="chartPopulationPie"></canvas>
      </div>
      <div class="stats-legend-list">
        <div class="stats-legend-item">
          <span class="stats-legend-dot" style="background:#2f7a4f;"></span>
          <span>Hommes</span>
          <strong>{{ pop_hommes_pct|default:"50,7" }}%</strong>
        </div>
        <div class="stats-legend-item">
          <span class="stats-legend-dot" style="background:#c9982e;"></span>
          <span>Femmes</span>
          <strong>{{ pop_femmes_pct|default:"49,3" }}%</strong>
        </div>
      </div>
    </div>
  </div>

  {% if repartition_infrastructures %}
  <div class="stats-section">
    <div class="stats-section-head">
      <div>
        <h2>Infrastructures par catégorie</h2>
        <p>{{ nb_infrastructures|floatformat:0 }} infrastructures recensées sur le territoire</p>
      </div>
      <div class="chart-toggle" data-target="infra">
        <button data-type="bar-h" class="active">Barres</button>
        <button data-type="bar-v">Colonnes</button>
        <button data-type="doughnut">Circulaire</button>
        <button data-type="polarArea">Polaire</button>
      </div>
    </div>
    <div class="chart-card">
      <canvas id="chartInfra"></canvas>
    </div>
  </div>
  {% endif %}

  {% if parcelles_par_quartier %}
  <div class="stats-section">
    <div class="stats-section-head">
      <div>
        <h2>Nombre de parcelles par quartier</h2>
        <p>Les 15 quartiers comptant le plus de parcelles cadastrées</p>
      </div>
      <div class="chart-toggle" data-target="quartiers">
        <button data-type="bar-v" class="active">Colonnes</button>
        <button data-type="bar-h">Barres</button>
        <button data-type="doughnut">Circulaire</button>
      </div>
    </div>
    <div class="chart-card">
      <canvas id="chartQuartiers"></canvas>
    </div>
  </div>
  {% endif %}
</section>
{% endblock %}

{% block extra_scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
(function () {
  if (typeof Chart === 'undefined') { return; }

  var PALETTE = ['#2f7a4f', '#c9982e', '#3a7d44', '#b3261e', '#6f6a5e', '#8a8276', '#a3791f', '#7a7266'];
  Chart.defaults.color = '#6f6a5e';

  function couleurs(n) {
    var out = [];
    for (var i = 0; i < n; i++) { out.push(PALETTE[i % PALETTE.length]); }
    return out;
  }

  var instances = {};

  function construireConfig(mode, labels, data, couleursDataset) {
    var palette = (couleursDataset && couleursDataset.length) ? couleursDataset : couleurs(labels.length);

    if (mode === 'bar-h' || mode === 'bar-v') {
      return {
        type: 'bar',
        data: { labels: labels, datasets: [{ data: data, backgroundColor: palette, borderRadius: 6 }] },
        options: {
          indexAxis: mode === 'bar-h' ? 'y' : 'x',
          plugins: { legend: { display: false } },
          scales: mode === 'bar-h'
            ? { x: { beginAtZero: true, ticks: { precision: 0 } } }
            : {
                y: { beginAtZero: true, ticks: { precision: 0 } },
                x: { ticks: { autoSkip: false, maxRotation: 60, minRotation: 30 } }
              }
        }
      };
    }
    if (mode === 'doughnut') {
      return {
        type: 'doughnut',
        data: { labels: labels, datasets: [{ data: data, backgroundColor: palette, borderWidth: 0 }] },
        options: { plugins: { legend: { position: 'bottom' } } }
      };
    }
    if (mode === 'polarArea') {
      return {
        type: 'polarArea',
        data: { labels: labels, datasets: [{ data: data, backgroundColor: palette }] },
        options: { plugins: { legend: { position: 'bottom' } } }
      };
    }
  }

  function afficher(canvasId, mode, labels, data, couleursDataset) {
    var el = document.getElementById(canvasId);
    if (!el) { return; }
    if (instances[canvasId]) { instances[canvasId].destroy(); }
    instances[canvasId] = new Chart(el, construireConfig(mode, labels, data, couleursDataset));
  }

  function initialiserToggle(target, canvasId, labels, data, couleursDataset, modeDefaut) {
    afficher(canvasId, modeDefaut, labels, data, couleursDataset);
    var groupe = document.querySelector('.chart-toggle[data-target="' + target + '"]');
    if (!groupe) { return; }
    groupe.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        groupe.querySelectorAll('button').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        afficher(canvasId, btn.getAttribute('data-type'), labels, data, couleursDataset);
      });
    });
  }

  var elPopulation = document.getElementById('chartPopulationPie');
  if (elPopulation) {
    new Chart(elPopulation, {
      type: 'doughnut',
      data: {
        labels: {{ chart_population_labels|default:"[]"|safe }},
        datasets: [{
          data: {{ chart_population_valeurs|default:"[]"|safe }},
          backgroundColor: ['#2f7a4f', '#c9982e'],
          borderWidth: 0
        }]
      },
      options: { plugins: { legend: { display: false } }, cutout: '68%' }
    });
  }

  initialiserToggle(
    'infra', 'chartInfra',
    {{ chart_infra_labels|default:"[]"|safe }},
    {{ chart_infra_valeurs|default:"[]"|safe }},
    {{ chart_infra_couleurs|default:"[]"|safe }},
    'bar-h'
  );

  initialiserToggle(
    'quartiers', 'chartQuartiers',
    {{ chart_quartiers_labels|default:"[]"|safe }},
    {{ chart_quartiers_valeurs|default:"[]"|safe }},
    null,
    'bar-v'
  );
})();
</script>
{% endblock %}
'''

chemin_html = "foncier/templates/foncier/statistiques.html"
with io.open(chemin_html, "w", encoding="utf-8", newline="\n") as f:
    f.write(nouveau_html)

print("OK : foncier/views.py et foncier/templates/foncier/statistiques.html ont ete reecrits.")