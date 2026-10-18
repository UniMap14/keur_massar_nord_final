# -*- coding: utf-8 -*-
"""
Ajoute les onglets thematiques sur le geoportail PUBLIC (meme regroupement
que sur l'admin), par-dessus l'accordeon deja en place.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) CSS des chips (identique a l'admin)
# ------------------------------------------------------------------
ANCIEN_CSS_ANCRE = '''  .geo-panel.is-collapsed .geo-panel-body { max-height: 0; opacity: 0; pointer-events: none; }'''

NOUVEAU_CSS = '''  .geo-panel.is-collapsed .geo-panel-body { max-height: 0; opacity: 0; pointer-events: none; }

  /* ===== Onglets thematiques au-dessus des panneaux (NOUVEAU) ===== */
  .geo-tab-bar { display: flex; gap: 6px; margin-bottom: 4px; flex-wrap: wrap; }
  .geo-tab-btn {
    flex: 1; border: 1.5px solid var(--geo-bordure); background: #fff; color: var(--geo-texte-mute);
    font-size: 12px; font-weight: 700; padding: 8px 10px; border-radius: 999px; cursor: pointer;
    transition: all .15s ease; white-space: nowrap;
  }
  .geo-tab-btn:hover { background: #faf6ec; }
  .geo-tab-btn.active { background: var(--geo-brun); border-color: var(--geo-brun); color: #fff; }'''

if '.geo-tab-btn{' in contenu or '.geo-tab-btn {' in contenu:
    pass
elif ANCIEN_CSS_ANCRE not in contenu:
    erreurs.append("ancre CSS introuvable (l'accordeon a-t-il bien ete applique avant ?)")
else:
    contenu = contenu.replace(ANCIEN_CSS_ANCRE, NOUVEAU_CSS, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) Conteneurs des barres d'onglets
# ------------------------------------------------------------------
if 'id="tabsGauche"' in contenu:
    pass
elif '<div class="geo-sidebar-left">' not in contenu:
    erreurs.append("conteneur geo-sidebar-left introuvable")
else:
    contenu = contenu.replace(
        '<div class="geo-sidebar-left">',
        '<div class="geo-sidebar-left">\n      <div class="geo-tab-bar" id="tabsGauche"></div>',
        1,
    )
    remplacements_ok += 1

if 'id="tabsDroite"' in contenu:
    pass
elif '<div class="geo-sidebar-right">' not in contenu:
    erreurs.append("conteneur geo-sidebar-right introuvable")
else:
    contenu = contenu.replace(
        '<div class="geo-sidebar-right">',
        '<div class="geo-sidebar-right">\n      <div class="geo-tab-bar" id="tabsDroite"></div>',
        1,
    )
    remplacements_ok += 1

# ------------------------------------------------------------------
# 3) JS : regroupement par ID (plus fiable ici, les titres ont deja un id)
# ------------------------------------------------------------------
ANCIEN_JS_ANCRE = '''<script>
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.geo-sidebar-left > .geo-panel, .geo-sidebar-right > .geo-panel').forEach(function (panel) {'''

NOUVEAU_JS = '''<script>
document.addEventListener('DOMContentLoaded', function () {
  const GROUPES = {
    gauche: {
      barre: 'tabsGauche',
      groupes: [
        { id: 'recherche', label: 'Recherche', ids: ['rechercheTitle', 'filtresTitle', 'rayonTitle'] },
        { id: 'analyse', label: 'Analyse', ids: ['sousDesservisTitle', 'voronoiTitle'] },
        { id: 'quartiers', label: 'Quartiers', ids: ['quartierTitle', 'comparaisonTitle'] },
      ],
    },
    droite: {
      barre: 'tabsDroite',
      groupes: [
        { id: 'vue', label: 'Vue', ids: ['statistiquesTitle', 'couchesTitle'] },
        { id: 'outils', label: 'Outils', ids: ['selectionTitle', 'itineraireTitle'] },
        { id: 'export', label: 'Export', ids: ['exportTitle'] },
      ],
    },
  };

  Object.values(GROUPES).forEach(function (config) {
    const barre = document.getElementById(config.barre);
    if (!barre) return;

    config.groupes.forEach(function (g) {
      g.ids.forEach(function (id) {
        const titreEl = document.getElementById(id);
        if (!titreEl) return;
        const panel = titreEl.closest('.geo-panel');
        if (panel) panel.dataset.group = g.id;
      });
    });

    const panels = document.querySelectorAll('[data-group]');

    function activerGroupe(groupeId) {
      panels.forEach(function (panel) {
        if (!config.groupes.some(function (g) { return g.id === panel.dataset.group; })) return;
        panel.style.display = (panel.dataset.group === groupeId) ? '' : 'none';
      });
      barre.querySelectorAll('.geo-tab-btn').forEach(function (btn) {
        btn.classList.toggle('active', btn.dataset.group === groupeId);
      });
    }

    config.groupes.forEach(function (g, index) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'geo-tab-btn';
      btn.dataset.group = g.id;
      btn.textContent = g.label;
      btn.addEventListener('click', function () { activerGroupe(g.id); });
      barre.appendChild(btn);
      if (index === 0) activerGroupe(g.id);
    });
  });

  document.querySelectorAll('.geo-sidebar-left > .geo-panel, .geo-sidebar-right > .geo-panel').forEach(function (panel) {'''

if 'const GROUPES = {' in contenu:
    pass
elif ANCIEN_JS_ANCRE not in contenu:
    erreurs.append("ancre JS introuvable (l'accordeon a-t-il bien ete applique avant ?)")
else:
    contenu = contenu.replace(ANCIEN_JS_ANCRE, NOUVEAU_JS, 1)
    remplacements_ok += 1

# ------------------------------------------------------------------
if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presentes).")