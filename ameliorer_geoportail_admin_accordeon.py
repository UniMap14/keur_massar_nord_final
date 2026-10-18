# -*- coding: utf-8 -*-
"""
Rend les panneaux lateraux du geoportail admin repliables (accordeon),
et fait passer la carte en premier sur mobile/tablette (<1150px).

Ne touche pas a la popup d'edition de parcelle (fp-edit-btn), qui est
une zone separee de la carte, pas un .geo-panel.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) Marquer les panneaux a replier par defaut (data-collapsed="true")
#    On garde ouverts par defaut : Rechercher, Filtres, Statistiques,
#    Couches SIG (les outils les plus utilises).
# ------------------------------------------------------------------
TITRES_A_REPLIER = [
    '<h2 class="geo-panel-title"><i class="fa-solid fa-circle-dot"></i> Rayon de couverture</h2>',
    '<h2 class="geo-panel-title"><i class="fa-solid fa-triangle-exclamation"></i> Zones sous-desservies</h2>',
    '<h2 class="geo-panel-title"><i class="fa-solid fa-map-location-dot"></i> Statistiques par quartier</h2>',
    '<h2 class="geo-panel-title"><i class="fa-solid fa-chart-column"></i> Comparaison des quartiers</h2>',
    '<h2 class="geo-panel-title"><i class="fa-solid fa-diagram-project"></i> Zones de desserte (Voronoï)</h2>',
    '<h2 class="geo-panel-title"><i class="fa-solid fa-draw-polygon"></i> Sélection spatiale</h2>',
    '<h2 class="geo-panel-title"><i class="fa-solid fa-location-crosshairs"></i> Itinéraire</h2>',
    '<h2 class="geo-panel-title"><i class="fa-solid fa-download"></i> Exporter</h2>',
]

for titre in TITRES_A_REPLIER:
    titre_marque = titre.replace(
        '<h2 class="geo-panel-title">',
        '<h2 class="geo-panel-title" data-collapsed="true">',
    )
    if titre_marque in contenu:
        continue  # deja applique
    if titre not in contenu:
        erreurs.append("titre introuvable : " + titre[:60])
        continue
    contenu = contenu.replace(titre, titre_marque)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) CSS accordeon + carte en premier sur mobile
# ------------------------------------------------------------------
ANCIEN_MEDIA = '''  @media (max-width: 1150px) {
    .geo-wrap { grid-template-columns: 1fr; height: auto; }
    .geo-map-col { min-height: 460px; }
    .geo-sidebar-left, .geo-sidebar-right { max-height: none; }
  }'''

NOUVEAU_MEDIA = '''  /* ===== Accordeon sur les panneaux lateraux (NOUVEAU) ===== */
  .geo-panel-title { cursor: pointer; user-select: none; }
  .geo-panel-chevron { margin-left: auto; font-size: 11px; color: var(--geo-texte-mute); transition: transform .2s ease; }
  .geo-panel.is-collapsed .geo-panel-chevron { transform: rotate(-90deg); }
  .geo-panel-body { overflow: hidden; max-height: 2000px; transition: max-height .25s ease, opacity .2s ease; opacity: 1; }
  .geo-panel.is-collapsed .geo-panel-body { max-height: 0; opacity: 0; pointer-events: none; }

  @media (max-width: 1150px) {
    .geo-wrap { grid-template-columns: 1fr; height: auto; }
    .geo-map-col { min-height: 460px; order: -1; }
    .geo-sidebar-left, .geo-sidebar-right { max-height: none; }
  }'''

if NOUVEAU_MEDIA in contenu:
    pass  # deja applique
elif ANCIEN_MEDIA not in contenu:
    erreurs.append("bloc media query introuvable tel quel")
else:
    contenu = contenu.replace(ANCIEN_MEDIA, NOUVEAU_MEDIA)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 3) JS qui construit l'accordeon au chargement de la page
# ------------------------------------------------------------------
ANCIEN_SCRIPT = '''<script>
  const URL_UPDATE_TEMPLATE = '{% url "parcelle_update_fiscal" 0 %}';'''

NOUVEAU_SCRIPT = '''<script>
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.geo-sidebar-left > .geo-panel, .geo-sidebar-right > .geo-panel').forEach(function (panel) {
    const titre = panel.querySelector('.geo-panel-title');
    if (!titre) return;

    // Regroupe tout le contenu du panneau (sauf le titre) dans un conteneur repliable.
    const corps = document.createElement('div');
    corps.className = 'geo-panel-body';
    while (titre.nextSibling) {
      corps.appendChild(titre.nextSibling);
    }
    panel.appendChild(corps);

    const chevron = document.createElement('i');
    chevron.className = 'fa-solid fa-chevron-down geo-panel-chevron';
    titre.appendChild(chevron);

    if (titre.dataset.collapsed === 'true') {
      panel.classList.add('is-collapsed');
    }

    titre.addEventListener('click', function () {
      panel.classList.toggle('is-collapsed');
    });
  });
});
</script>
<script>
  const URL_UPDATE_TEMPLATE = '{% url "parcelle_update_fiscal" 0 %}';'''

if NOUVEAU_SCRIPT in contenu:
    pass  # deja applique
elif ANCIEN_SCRIPT not in contenu:
    erreurs.append("balise script d'origine introuvable telle quelle")
else:
    contenu = contenu.replace(ANCIEN_SCRIPT, NOUVEAU_SCRIPT)
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