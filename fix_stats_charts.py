# -*- coding: utf-8 -*-
import io

# ============================================================
# 1) foncier/views.py : enrichir statistiques() avec les donnees
#    necessaires aux graphiques (JSON pret pour Chart.js).
# ============================================================
chemin_views = "foncier/views.py"
with io.open(chemin_views, "r", encoding="utf-8") as f:
    contenu_views = f.read()

ancienne_fonction = """def statistiques(request):
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

    # --- Infrastructures publiques réellement recensées ---
    context['nb_infrastructures'] = Infrastructure.objects.count()
    context['repartition_infrastructures'] = (
        CategorieInfrastructure.objects
        .annotate(total=Count('infrastructures'))
        .filter(total__gt=0)
        .order_by('-total')
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

nb = contenu_views.count(ancienne_fonction)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre de statistiques() trouvee {nb} fois (attendu 1) dans views.py. "
        f"Rien n'a ete modifie."
    )
contenu_views = contenu_views.replace(ancienne_fonction, nouvelle_fonction)

# ============================================================
# 2) foncier/templates/foncier/statistiques.html : ajout des
#    graphiques Chart.js.
# ============================================================
chemin_html = "foncier/templates/foncier/statistiques.html"
with io.open(chemin_html, "r", encoding="utf-8") as f:
    contenu_html = f.read()

# --- 2a) CSS : ajouter les classes des cartes-graphiques ---
ancien_css = """  @media (max-width: 900px){ .stat-page-grid{ grid-template-columns:repeat(2,1fr); } }
  @media (max-width: 520px){ .stat-page-grid{ grid-template-columns:1fr; } }
</style>"""

nouveau_css = """  @media (max-width: 900px){ .stat-page-grid{ grid-template-columns:repeat(2,1fr); } }
  @media (max-width: 520px){ .stat-page-grid{ grid-template-columns:1fr; } }

  .stat-chart-grid{
    display:grid; grid-template-columns:repeat(2,1fr); gap:24px; margin-top:24px;
  }
  .stat-chart-card{
    background:#fff; border:1px solid var(--border); border-radius:var(--radius);
    padding:24px; box-shadow:0 2px 10px rgba(0,0,0,.05);
  }
  .stat-chart-card h3{
    font-size:15px; font-weight:700; margin:0 0 16px;
  }
  .stat-chart-card canvas{ max-height:280px; }
  .stat-chart-card.stat-chart-wide{ grid-column:1 / -1; }
  @media (max-width: 900px){ .stat-chart-grid{ grid-template-columns:1fr; } }
</style>"""

nb = contenu_html.count(ancien_css)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre CSS trouvee {nb} fois (attendu 1) dans statistiques.html. "
        f"Rien n'a ete modifie."
    )
contenu_html = contenu_html.replace(ancien_css, nouveau_css)

# --- 2b) Graphique population (Hommes / Femmes), juste avant le
#     bloc "{% if nb_parcelles %}" ---
ancien_pop = """  </div>

  {% if nb_parcelles %}"""

nouveau_pop = """  </div>

  <div class="stat-chart-grid" style="margin-top:28px;">
    <div class="stat-chart-card">
      <h3>Répartition de la population</h3>
      <canvas id="chartPopulationPie"></canvas>
    </div>
  </div>

  {% if nb_parcelles %}"""

nb = contenu_html.count(ancien_pop)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre population trouvee {nb} fois (attendu 1) dans statistiques.html. "
        f"Rien n'a ete modifie."
    )
contenu_html = contenu_html.replace(ancien_pop, nouveau_pop)

# --- 2c) Occupation du sol + parcelles par quartier +
#     infrastructures par categorie : remplace les deux blocs
#     existants par une version enrichie avec graphiques ---
ancien_blocs = """  {% if repartition_occupation %}
  <div style="max-width:640px; margin-top:36px;">
    <h3 style="font-size:15px; font-weight:700; margin-bottom:16px;">Répartition par occupation du sol</h3>
    {% for r in repartition_occupation %}
    <div style="margin-bottom:14px;">
      <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:5px;">
        <span>{{ r.label }}</span>
        <span style="font-weight:600; color:var(--ink-quiet, #6f6a5e);">{{ r.total|floatformat:0 }} ({{ r.pourcentage }}%)</span>
      </div>
      <div style="background:rgba(0,0,0,0.06); border-radius:999px; height:8px; overflow:hidden;">
        <div style="background:var(--gold, #c9982e); height:100%; width:{{ r.largeur_barre }}%; border-radius:999px;"></div>
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if repartition_infrastructures %}
  <div style="max-width:640px; margin-top:36px;">
    <h3 style="font-size:15px; font-weight:700; margin-bottom:16px;">Infrastructures par catégorie</h3>
    <div style="display:flex; flex-wrap:wrap; gap:10px;">
      {% for cat in repartition_infrastructures %}
      <div style="background:#fff; border:1px solid rgba(0,0,0,0.08); border-radius:10px; padding:10px 16px; font-size:13px; display:flex; align-items:center; gap:8px;">
        {% if cat.icone %}<i class="fa-solid {{ cat.icone }}"></i>{% endif %}
        <span>{{ cat.label }}</span>
        <strong style="color:var(--green-dark, #3c2a20);">{{ cat.total }}</strong>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}"""

nouveaux_blocs = """  {% if repartition_occupation %}
  <h3 style="font-size:15px; font-weight:700; margin-top:36px; margin-bottom:4px;">Répartition par occupation du sol</h3>
  <div class="stat-chart-grid">
    <div class="stat-chart-card">
      <h3>En barres</h3>
      <canvas id="chartOccupationBarres"></canvas>
    </div>
    <div class="stat-chart-card">
      <h3>En proportion</h3>
      <canvas id="chartOccupationDonut"></canvas>
    </div>
  </div>
  <div style="max-width:640px; margin-top:24px;">
    {% for r in repartition_occupation %}
    <div style="margin-bottom:14px;">
      <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:5px;">
        <span>{{ r.label }}</span>
        <span style="font-weight:600; color:var(--ink-quiet, #6f6a5e);">{{ r.total|floatformat:0 }} ({{ r.pourcentage }}%)</span>
      </div>
      <div style="background:rgba(0,0,0,0.06); border-radius:999px; height:8px; overflow:hidden;">
        <div style="background:var(--gold, #c9982e); height:100%; width:{{ r.largeur_barre }}%; border-radius:999px;"></div>
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if parcelles_par_quartier %}
  <h3 style="font-size:15px; font-weight:700; margin-top:36px; margin-bottom:4px;">Nombre de parcelles par quartier (top 15)</h3>
  <div class="stat-chart-grid">
    <div class="stat-chart-card stat-chart-wide">
      <canvas id="chartQuartiersBarres"></canvas>
    </div>
  </div>
  {% endif %}

  {% if repartition_infrastructures %}
  <h3 style="font-size:15px; font-weight:700; margin-top:36px; margin-bottom:4px;">Infrastructures par catégorie</h3>
  <div class="stat-chart-grid">
    <div class="stat-chart-card">
      <h3>En barres</h3>
      <canvas id="chartInfraBarres"></canvas>
    </div>
    <div class="stat-chart-card">
      <h3>En proportion</h3>
      <canvas id="chartInfraDonut"></canvas>
    </div>
  </div>
  <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:24px;">
    {% for cat in repartition_infrastructures %}
    <div style="background:#fff; border:1px solid rgba(0,0,0,0.08); border-radius:10px; padding:10px 16px; font-size:13px; display:flex; align-items:center; gap:8px;">
      {% if cat.icone %}<i class="fa-solid {{ cat.icone }}"></i>{% endif %}
      <span>{{ cat.label }}</span>
      <strong style="color:var(--green-dark, #3c2a20);">{{ cat.total }}</strong>
    </div>
    {% endfor %}
  </div>
  {% endif %}"""

nb = contenu_html.count(ancien_blocs)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre occupation/infrastructures trouvee {nb} fois (attendu 1) "
        f"dans statistiques.html. Rien n'a ete modifie."
    )
contenu_html = contenu_html.replace(ancien_blocs, nouveaux_blocs)

# --- 2d) Ajout du bloc extra_scripts (Chart.js + construction des
#     graphiques) a la toute fin du fichier ---
ancienne_fin = """  {% endif %}
  {% endif %}
</section>
{% endblock %}"""

nouvelle_fin = """  {% endif %}
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

  var elPopulation = document.getElementById('chartPopulationPie');
  if (elPopulation) {
    new Chart(elPopulation, {
      type: 'pie',
      data: {
        labels: {{ chart_population_labels|default:"[]"|safe }},
        datasets: [{
          data: {{ chart_population_valeurs|default:"[]"|safe }},
          backgroundColor: ['#2f7a4f', '#c9982e'],
          borderWidth: 0
        }]
      },
      options: { plugins: { legend: { position: 'bottom' } } }
    });
  }

  var elOccupationBarres = document.getElementById('chartOccupationBarres');
  if (elOccupationBarres) {
    var labelsOccupation = {{ chart_occupation_labels|default:"[]"|safe }};
    new Chart(elOccupationBarres, {
      type: 'bar',
      data: {
        labels: labelsOccupation,
        datasets: [{
          label: 'Parcelles',
          data: {{ chart_occupation_valeurs|default:"[]"|safe }},
          backgroundColor: couleurs(labelsOccupation.length),
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  }

  var elOccupationDonut = document.getElementById('chartOccupationDonut');
  if (elOccupationDonut) {
    var labelsOccupationD = {{ chart_occupation_labels|default:"[]"|safe }};
    new Chart(elOccupationDonut, {
      type: 'doughnut',
      data: {
        labels: labelsOccupationD,
        datasets: [{
          data: {{ chart_occupation_valeurs|default:"[]"|safe }},
          backgroundColor: couleurs(labelsOccupationD.length),
          borderWidth: 0
        }]
      },
      options: { plugins: { legend: { position: 'bottom' } } }
    });
  }

  var elQuartiers = document.getElementById('chartQuartiersBarres');
  if (elQuartiers) {
    var labelsQuartiers = {{ chart_quartiers_labels|default:"[]"|safe }};
    new Chart(elQuartiers, {
      type: 'bar',
      data: {
        labels: labelsQuartiers,
        datasets: [{
          label: 'Parcelles',
          data: {{ chart_quartiers_valeurs|default:"[]"|safe }},
          backgroundColor: '#2f7a4f',
          borderRadius: 6
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { autoSkip: false, maxRotation: 60, minRotation: 40 } },
          y: { beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
  }

  var elInfraBarres = document.getElementById('chartInfraBarres');
  if (elInfraBarres) {
    var labelsInfra = {{ chart_infra_labels|default:"[]"|safe }};
    var couleursInfra = {{ chart_infra_couleurs|default:"[]"|safe }};
    new Chart(elInfraBarres, {
      type: 'bar',
      data: {
        labels: labelsInfra,
        datasets: [{
          label: 'Infrastructures',
          data: {{ chart_infra_valeurs|default:"[]"|safe }},
          backgroundColor: couleursInfra.length ? couleursInfra : couleurs(labelsInfra.length),
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  }

  var elInfraDonut = document.getElementById('chartInfraDonut');
  if (elInfraDonut) {
    var labelsInfraD = {{ chart_infra_labels|default:"[]"|safe }};
    var couleursInfraD = {{ chart_infra_couleurs|default:"[]"|safe }};
    new Chart(elInfraDonut, {
      type: 'doughnut',
      data: {
        labels: labelsInfraD,
        datasets: [{
          data: {{ chart_infra_valeurs|default:"[]"|safe }},
          backgroundColor: couleursInfraD.length ? couleursInfraD : couleurs(labelsInfraD.length),
          borderWidth: 0
        }]
      },
      options: { plugins: { legend: { position: 'bottom' } } }
    });
  }
})();
</script>
{% endblock %}"""

nb = contenu_html.count(ancienne_fin)
if nb != 1:
    raise SystemExit(
        f"ARRET : ancre de fin de fichier trouvee {nb} fois (attendu 1) "
        f"dans statistiques.html. Rien n'a ete modifie."
    )
contenu_html = contenu_html.replace(ancienne_fin, nouvelle_fin)

# ============================================================
# 3) Ecriture finale (seulement si TOUTES les ancres ont ete
#    validees ci-dessus : rien n'est ecrit en cas d'erreur).
# ============================================================
with io.open(chemin_views, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_views)

with io.open(chemin_html, "w", encoding="utf-8", newline="\n") as f:
    f.write(contenu_html)

print("OK : foncier/views.py et foncier/templates/foncier/statistiques.html ont ete mis a jour.")