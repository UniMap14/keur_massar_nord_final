# -*- coding: utf-8 -*-
"""
Regroupe les panneaux lateraux du geoportail admin par onglets thematiques
(Recherche / Analyse / Quartiers a gauche, Vue / Outils / Export a droite).
S'appuie sur l'accordeon deja en place (ne le modifie pas).

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) CSS des onglets (pills, meme style que le switch de fond de carte)
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

if NOUVEAU_CSS in contenu:
    pass
elif ANCIEN_CSS_ANCRE not in contenu:
    erreurs.append("ancre CSS introuvable (l'accordeon a-t-il bien ete applique avant ?)")
else:
    contenu = contenu.replace(ANCIEN_CSS_ANCRE, NOUVEAU_CSS)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) Conteneurs des barres d'onglets (vides, remplis par JS)
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
# 3) JS qui construit les onglets et filtre les panneaux
# ------------------------------------------------------------------
ANCIEN_JS_ANCRE = '''});
</script>
<script>
  const URL_UPDATE_TEMPLATE = '{% url "parcelle_update_fiscal" 0 %}';'''

NOUVEAU_JS = '''});
</script>
<script>
document.addEventListener('DOMContentLoaded', function () {
  const GROUPES = {
    gauche: {
      conteneur: '.geo-sidebar-left',
      barre: 'tabsGauche',
      groupes: [
        { id: 'recherche', label: 'Recherche', titres: ['Rechercher', 'Filtres', 'Rayon de couverture'] },
        { id: 'analyse', label: 'Analyse', titres: ['Zones sous-desservies', 'Zones de desserte (Voronoï)'] },
        { id: 'quartiers', label: 'Quartiers', titres: ['Statistiques par quartier', 'Comparaison des quartiers'] },
      ],
    },
    droite: {
      conteneur: '.geo-sidebar-right',
      barre: 'tabsDroite',
      groupes: [
        { id: 'vue', label: 'Vue', titres: ['Statistiques', 'Couches SIG'] },
        { id: 'outils', label: 'Outils', titres: ['Sélection spatiale', 'Itinéraire'] },
        { id: 'export', label: 'Export', titres: ['Exporter'] },
      ],
    },
  };

  Object.values(GROUPES).forEach(function (config) {
    const barre = document.getElementById(config.barre);
    const panels = document.querySelectorAll(config.conteneur + ' > .geo-panel');
    if (!barre || !panels.length) return;

    // Associe chaque panneau a son groupe, d'apres le texte de son titre.
    panels.forEach(function (panel) {
      const titreEl = panel.querySelector('.geo-panel-title');
      if (!titreEl) return;
      const texte = titreEl.textContent.trim();
      const groupe = config.groupes.find(function (g) { return g.titres.indexOf(texte) !== -1; });
      panel.dataset.group = groupe ? groupe.id : config.groupes[0].id;
    });

    function activerGroupe(groupeId) {
      panels.forEach(function (panel) {
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
});
</script>
<script>
  const URL_UPDATE_TEMPLATE = '{% url "parcelle_update_fiscal" 0 %}';'''

if 'const GROUPES = {' in contenu:
    pass
elif ANCIEN_JS_ANCRE not in contenu:
    erreurs.append("ancre JS introuvable (l'accordeon a-t-il bien ete applique avant ?)")
else:
    contenu = contenu.replace(ANCIEN_JS_ANCRE, NOUVEAU_JS)
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