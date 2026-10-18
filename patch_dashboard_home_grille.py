# -*- coding: utf-8 -*-
"""
Phase 3 (template) : reorganise le tableau de bord en grille compacte 3
colonnes (comme l'image de reference), ajoute une vraie mini-carte
Leaflet (donnees reelles : superficie, zones, parcelles actives) et un
vrai fil d'activite recente (evenements reels, voir
patch_dashboard_views_activite.py, qui doit etre applique AVANT ce
script).

Principe : aucun panneau existant n'est supprime ni recree -- chacun
recoit juste une classe CSS "cell-xxx" qui lui donne sa position dans
une grille CSS (.dashboard-grid), donc le HTML garde son organisation
actuelle et seule l'apparence change. Deux nouveaux panneaux sont
ajoutes (mini-carte, activite recente).

Toutes les ancres de ce script sont 100% ASCII (aucun caractere
accentue) : le fichier source contient des accents, mais le rendu
PowerShell colle dans le chat peut les deformer (mojibake), donc on
evite de s'appuyer dessus pour la comparaison de texte.

Idempotent : si le patch est deja applique (marqueur "dashboard-grid"
present), le script le signale et ne touche a rien.

Pre-requis :
  - patch_dashboard_home_design.py (deja applique)
  - patch_dashboard_home_kpis.py (deja applique)
  - patch_dashboard_views_activite.py (deja applique, pour le contexte
    activite_recente / map_superficie_km2 / map_nb_zones /
    map_nb_parcelles_actives)
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

DEJA_APPLIQUE = "dashboard-grid" in texte

# ---------------------------------------------------------------------
# 1) CSS : nouvelles regles pour la grille, la mini-carte, le fil d'activite
# ---------------------------------------------------------------------
ANCRE_CSS = """    .chart-legend-list .legend-pct { font-weight: 700; color: var(--ink-quiet, #7a7266); }
</style>
{% endblock %}"""
AJOUT_CSS = """    .chart-legend-list .legend-pct { font-weight: 700; color: var(--ink-quiet, #7a7266); }

    /* ===== Grille compacte du tableau de bord (phase 3) ===== */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 20px;
        align-items: stretch;
    }
    .cell-taux { grid-column: 1; grid-row: 1; }
    .cell-evolution { grid-column: 2; grid-row: 1; }
    .cell-geo-banner { grid-column: 3; grid-row: 1; margin: 0; flex-direction: column; align-items: flex-start; text-align: left; }
    .cell-geo-banner .geo-access-btn { margin-top: 10px; }
    .cell-stats-row { grid-column: 1 / 3; grid-row: 2; margin: 0; }
    .cell-map { grid-column: 3; grid-row: 2; }
    .cell-paiements { grid-column: 1; grid-row: 3; }
    .cell-retardataires { grid-column: 2; grid-row: 3; }
    .cell-activite { grid-column: 3; grid-row: 3; }
    .cell-quick-actions { grid-column: 1 / -1; grid-row: 4; }

    @media (max-width: 1100px) {
        .dashboard-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .cell-taux, .cell-evolution, .cell-geo-banner, .cell-map,
        .cell-paiements, .cell-retardataires, .cell-activite {
            grid-column: auto; grid-row: auto;
        }
        .cell-stats-row, .cell-quick-actions { grid-column: 1 / -1; grid-row: auto; }
    }
    @media (max-width: 720px) {
        .dashboard-grid { grid-template-columns: 1fr; }
        .cell-stats-row, .cell-quick-actions { grid-column: 1; }
    }

    /* ===== Mini-carte de la commune ===== */
    .mini-map-canvas { height: 180px; width: 100%; }
    .mini-map-stats {
        display: flex;
        justify-content: space-around;
        padding: 14px 10px;
        border-top: 1px solid var(--border, #eee6d6);
    }
    .mini-map-stats > div { text-align: center; }
    .mini-map-stats .mm-value { display: block; font-size: 16px; font-weight: 800; color: var(--ink, #2a2620); }
    .mini-map-stats .mm-label { display: block; font-size: 10.5px; color: var(--ink-quiet, #7a7266); text-transform: uppercase; letter-spacing: .04em; }

    /* ===== Fil d'activite recente ===== */
    .activity-feed { list-style: none; margin: 0; padding: 14px 18px; display: flex; flex-direction: column; gap: 14px; }
    .activity-feed li { display: flex; align-items: flex-start; gap: 12px; }
    .activity-icon {
        width: 30px; height: 30px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; flex-shrink: 0;
    }
    .activity-icon.tone-green { background: rgba(58,125,68,0.12); color: #3a7d44; }
    .activity-icon.tone-gold { background: rgba(201,152,46,0.14); color: #a3791f; }
    .activity-icon.tone-red { background: rgba(179,38,30,0.10); color: #b3261e; }
    .activity-icon.tone-blue { background: rgba(45,100,160,0.10); color: #2d64a0; }
    .activity-icon.tone-purple { background: rgba(123,63,160,0.12); color: #7b3fa0; }
    .activity-text { flex: 1; }
    .activity-title { font-size: 12.5px; color: var(--ink, #2a2620); line-height: 1.4; }
    .activity-time { font-size: 11px; color: var(--ink-quiet, #7a7266); margin-top: 2px; }
</style>
{% endblock %}"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# 2) CSS : la tuile Geoportail ne doit plus forcer toute la largeur
#    (elle devient une cellule normale de la grille, cf. .cell-geo-banner)
# ---------------------------------------------------------------------
ANCRE_SPAN = """    .geo-access-card {
        grid-column: 1 / -1;
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);"""
AJOUT_SPAN = """    .geo-access-card {
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_SPAN not in texte:
    erreurs.append("ANCRE_SPAN introuvable")
else:
    texte = texte.replace(ANCRE_SPAN, AJOUT_SPAN, 1)

# ---------------------------------------------------------------------
# 3) HTML : supprimer la tuile Geoportail de son emplacement d'origine
#    (tout en haut du contenu) -- elle sera reinseree dans la grille
#    juste apres, avec sa nouvelle classe cell-geo-banner.
# ---------------------------------------------------------------------
ANCRE_SUPPR_GEO = """{% block content %}

<a href="{% url 'geoportail_admin' %}" class="geo-access-card">
  <div class="geo-access-left">
    <div class="geo-access-icon"><i class="fa-solid fa-map-location-dot"></i></div>
    <div class="geo-access-text">
      <h3>Geoportail SIG</h3>
      <p>Carte cadastrale complete, outils SIG et edition des parcelles en plein ecran.</p>
    </div>
  </div>
  <span class="geo-access-btn">Acceder au Geoportail <i class="fa-solid fa-arrow-right"></i></span>
</a>

<div class="kpi-grid">"""
AJOUT_SUPPR_GEO = """{% block content %}

<div class="kpi-grid">"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_SUPPR_GEO not in texte:
    erreurs.append("ANCRE_SUPPR_GEO introuvable")
else:
    texte = texte.replace(ANCRE_SUPPR_GEO, AJOUT_SUPPR_GEO, 1)

# ---------------------------------------------------------------------
# 4) HTML : ouverture de la grille + reinsertion de la tuile Geoportail
#    (cell-geo-banner) juste avant le panneau "Taux de recouvrement"
# ---------------------------------------------------------------------
ANCRE_OUVRE_GRILLE = """  </a>
</div>

{% if peut_fiscal %}
<!-- ============ TAUX DE RECOUVREMENT ============ -->"""
AJOUT_OUVRE_GRILLE = """  </a>
</div>

<div class="dashboard-grid">
<a href="{% url 'geoportail_admin' %}" class="geo-access-card cell-geo-banner">
  <div class="geo-access-left">
    <div class="geo-access-icon"><i class="fa-solid fa-map-location-dot"></i></div>
    <div class="geo-access-text">
      <h3>Geoportail SIG</h3>
      <p>Carte cadastrale complete, outils SIG et edition des parcelles en plein ecran.</p>
    </div>
  </div>
  <span class="geo-access-btn">Acceder au Geoportail <i class="fa-solid fa-arrow-right"></i></span>
</a>

{% if peut_fiscal %}
<!-- ============ TAUX DE RECOUVREMENT ============ -->"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_OUVRE_GRILLE not in texte:
    erreurs.append("ANCRE_OUVRE_GRILLE introuvable")
else:
    texte = texte.replace(ANCRE_OUVRE_GRILLE, AJOUT_OUVRE_GRILLE, 1)

# ---------------------------------------------------------------------
# 5) HTML : classe cell-taux sur le panneau "Taux de recouvrement"
# ---------------------------------------------------------------------
ANCRE_TAUX = """<!-- ============ TAUX DE RECOUVREMENT ============ -->
<div class="panel">"""
AJOUT_TAUX = """<!-- ============ TAUX DE RECOUVREMENT ============ -->
<div class="panel cell-taux">"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_TAUX not in texte:
    erreurs.append("ANCRE_TAUX introuvable")
else:
    texte = texte.replace(ANCRE_TAUX, AJOUT_TAUX, 1)

# ---------------------------------------------------------------------
# 6) HTML : classe cell-evolution sur le panneau "Evolution des paiements"
# ---------------------------------------------------------------------
ANCRE_EVOL = """<!-- ============ GRAPHIQUES ============ -->
<div class="panel">"""
AJOUT_EVOL = """<!-- ============ GRAPHIQUES ============ -->
<div class="panel cell-evolution">"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_EVOL not in texte:
    erreurs.append("ANCRE_EVOL introuvable")
else:
    texte = texte.replace(ANCRE_EVOL, AJOUT_EVOL, 1)

# ---------------------------------------------------------------------
# 7) HTML : classe cell-stats-row sur la ligne zones + taxes
# ---------------------------------------------------------------------
ANCRE_STATSROW = '<div class="stats-charts-row">'
AJOUT_STATSROW = '<div class="stats-charts-row cell-stats-row">'
if DEJA_APPLIQUE:
    pass
elif ANCRE_STATSROW not in texte:
    erreurs.append("ANCRE_STATSROW introuvable")
else:
    texte = texte.replace(ANCRE_STATSROW, AJOUT_STATSROW, 1)

# ---------------------------------------------------------------------
# 8) HTML : nouvelle mini-carte (Leaflet) + classe cell-quick-actions
#    sur le bandeau "Que voulez-vous faire ?"
# ---------------------------------------------------------------------
ANCRE_MINICARTE = """{% endif %}
<!-- ============ ACTIONS RAPIDES ============ -->
<div class="panel quick-actions-panel">"""
AJOUT_MINICARTE = """{% endif %}
<!-- ============ MINI CARTE ============ -->
<div class="panel cell-map">
  <div class="panel-header">
    <h2><i class="fa-solid fa-map"></i> Carte de la commune</h2>
    <a href="{% url 'geoportail_admin' %}" class="btn btn-outline btn-sm">Voir tout</a>
  </div>
  <div class="panel-body flush">
    <div id="miniCarteCommune" class="mini-map-canvas"></div>
    <div class="mini-map-stats">
      <div><span class="mm-value">{{ map_superficie_km2 }}</span><span class="mm-label">km2</span></div>
      <div><span class="mm-value">{{ map_nb_zones }}</span><span class="mm-label">Zones</span></div>
      <div><span class="mm-value">{{ map_nb_parcelles_actives }}</span><span class="mm-label">Parcelles actives</span></div>
    </div>
  </div>
</div>

<!-- ============ ACTIONS RAPIDES ============ -->
<div class="panel quick-actions-panel cell-quick-actions">"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_MINICARTE not in texte:
    erreurs.append("ANCRE_MINICARTE introuvable")
else:
    texte = texte.replace(ANCRE_MINICARTE, AJOUT_MINICARTE, 1)

# ---------------------------------------------------------------------
# 9) HTML : classe cell-paiements sur "Derniers paiements"
# ---------------------------------------------------------------------
ANCRE_PAIEMENTS = """<div class="panel">
  <div class="panel-header">
    <h2><i class="fa-solid fa-receipt"></i> Derniers paiements</h2>"""
AJOUT_PAIEMENTS = """<div class="panel cell-paiements">
  <div class="panel-header">
    <h2><i class="fa-solid fa-receipt"></i> Derniers paiements</h2>"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_PAIEMENTS not in texte:
    erreurs.append("ANCRE_PAIEMENTS introuvable")
else:
    texte = texte.replace(ANCRE_PAIEMENTS, AJOUT_PAIEMENTS, 1)

# ---------------------------------------------------------------------
# 10) HTML : classe cell-retardataires sur "Parcelles en retard"
# ---------------------------------------------------------------------
ANCRE_RETARD = """<div class="panel">
  <div class="panel-header">
    <h2><i class="fa-solid fa-scale-unbalanced"></i> Parcelles en retard"""
AJOUT_RETARD = """<div class="panel cell-retardataires">
  <div class="panel-header">
    <h2><i class="fa-solid fa-scale-unbalanced"></i> Parcelles en retard"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_RETARD not in texte:
    erreurs.append("ANCRE_RETARD introuvable")
else:
    texte = texte.replace(ANCRE_RETARD, AJOUT_RETARD, 1)

# ---------------------------------------------------------------------
# 11) HTML : nouveau panneau "Activite recente" + fermeture de la grille
#     juste avant le script d'animation de la barre de recouvrement
# ---------------------------------------------------------------------
ANCRE_ACTIVITE = """{% endif %}
<script>
document.addEventListener('DOMContentLoaded', function () {
"""
AJOUT_ACTIVITE = """{% endif %}
<!-- ============ ACTIVITE RECENTE ============ -->
<div class="panel cell-activite">
  <div class="panel-header">
    <h2><i class="fa-solid fa-clock-rotate-left"></i> Activite recente</h2>
  </div>
  <div class="panel-body flush">
    {% if activite_recente %}
    <ul class="activity-feed">
      {% for item in activite_recente %}
      <li>
        <span class="activity-icon tone-{{ item.tone }}"><i class="fa-solid {{ item.icone }}"></i></span>
        <div class="activity-text">
          <div class="activity-title">{{ item.titre }}</div>
          <div class="activity-time">Il y a {{ item.date|timesince }}</div>
        </div>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <div class="empty-state">
      <div class="icon icon-neutral"><i class="fa-regular fa-circle"></i></div>
      Aucune activite recente.
    </div>
    {% endif %}
  </div>
</div>

</div>

<script>
document.addEventListener('DOMContentLoaded', function () {
"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_ACTIVITE not in texte:
    erreurs.append("ANCRE_ACTIVITE introuvable")
else:
    texte = texte.replace(ANCRE_ACTIVITE, AJOUT_ACTIVITE, 1)

# ---------------------------------------------------------------------
# 12) HTML : feuille de style Leaflet (CSS) dans extra_head
# ---------------------------------------------------------------------
ANCRE_LEAFLET_CSS = """{% block extra_head %}
<style>"""
AJOUT_LEAFLET_CSS = """{% block extra_head %}
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_LEAFLET_CSS not in texte:
    erreurs.append("ANCRE_LEAFLET_CSS introuvable")
else:
    texte = texte.replace(ANCRE_LEAFLET_CSS, AJOUT_LEAFLET_CSS, 1)

# ---------------------------------------------------------------------
# 13) JS : script Leaflet (apres Chart.js) dans extra_js
# ---------------------------------------------------------------------
ANCRE_LEAFLET_JS = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>\n'
AJOUT_LEAFLET_JS = (
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>\n'
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n'
)
if DEJA_APPLIQUE:
    pass
elif ANCRE_LEAFLET_JS not in texte:
    erreurs.append("ANCRE_LEAFLET_JS introuvable")
else:
    texte = texte.replace(ANCRE_LEAFLET_JS, AJOUT_LEAFLET_JS, 1)

# ---------------------------------------------------------------------
# 14) JS : initialisation de la mini-carte, juste avant la fin du bloc
#     extra_js (pas de ligne vide avant {% endblock %} a cet endroit
#     precis, ce qui le distingue de la fin du bloc content)
# ---------------------------------------------------------------------
ANCRE_INIT_CARTE = """});
</script>
{% endblock %}"""
AJOUT_INIT_CARTE = """    var elMiniMap = document.getElementById('miniCarteCommune');
    if (elMiniMap && window.L) {
        var miniMap = L.map('miniCarteCommune', {
            zoomControl: false,
            attributionControl: false,
            dragging: false,
            scrollWheelZoom: false,
            doubleClickZoom: false,
            boxZoom: false,
            keyboard: false,
        }).setView([14.79, -17.31], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
        }).addTo(miniMap);

        L.circle([14.79, -17.31], {
            radius: 2500,
            color: '#c9982e',
            weight: 2,
            fillColor: '#c9982e',
            fillOpacity: 0.12,
        }).addTo(miniMap);

        L.marker([14.79, -17.31]).addTo(miniMap).bindPopup('Keur Massar Nord');
    }
});
</script>
{% endblock %}"""
if DEJA_APPLIQUE:
    pass
elif ANCRE_INIT_CARTE not in texte:
    erreurs.append("ANCRE_INIT_CARTE introuvable")
else:
    texte = texte.replace(ANCRE_INIT_CARTE, AJOUT_INIT_CARTE, 1)

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
    print("OK : dashboard/home.html mis a jour (grille compacte + mini-carte + fil d'activite).")