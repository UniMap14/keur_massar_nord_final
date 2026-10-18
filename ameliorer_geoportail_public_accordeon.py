# -*- coding: utf-8 -*-
"""
Ajoute l'accordeon sur les panneaux lateraux du geoportail PUBLIC (meme
logique que sur l'admin), sans toucher au guide vocal deja attache aux
boutons de titre (VoiceGuide.speakSection). Les deux listeners coexistent :
le clic replie/deplie ET lit l'explication.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# ------------------------------------------------------------------
# 1) Marquer les panneaux a replier par defaut (via leur id, deja unique)
# ------------------------------------------------------------------
IDS_A_REPLIER = [
    "rayonTitle", "sousDesservisTitle", "quartierTitle", "comparaisonTitle",
    "voronoiTitle", "selectionTitle", "itineraireTitle", "exportTitle",
]

for id_titre in IDS_A_REPLIER:
    ancien = f'<button type="button" class="geo-panel-title" id="{id_titre}">'
    nouveau = f'<button type="button" class="geo-panel-title" id="{id_titre}" data-collapsed="true">'
    if nouveau in contenu:
        continue
    if ancien not in contenu:
        erreurs.append("bouton introuvable : " + id_titre)
        continue
    contenu = contenu.replace(ancien, nouveau)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 2) CSS accordeon + carte en premier sur mobile
# ------------------------------------------------------------------
ANCIEN_MEDIA = '''  @media (max-width: 1150px) {
    .geo-wrap { grid-template-columns: 1fr; }
    .geo-map-col { min-height: 460px; }
    .geo-sidebar-left, .geo-sidebar-right { max-height: none; }
  }'''

NOUVEAU_MEDIA = '''  /* ===== Accordeon sur les panneaux lateraux (NOUVEAU) ===== */
  .geo-panel-chevron { margin-left: auto; font-size: 11px; color: var(--geo-texte-mute); transition: transform .2s ease; }
  .geo-panel.is-collapsed .geo-panel-chevron { transform: rotate(-90deg); }
  .geo-panel-body { overflow: hidden; max-height: 2000px; transition: max-height .25s ease, opacity .2s ease; opacity: 1; }
  .geo-panel.is-collapsed .geo-panel-body { max-height: 0; opacity: 0; pointer-events: none; }

  @media (max-width: 1150px) {
    .geo-wrap { grid-template-columns: 1fr; }
    .geo-map-col { min-height: 460px; order: -1; }
    .geo-sidebar-left, .geo-sidebar-right { max-height: none; }
  }'''

if NOUVEAU_MEDIA in contenu:
    pass
elif ANCIEN_MEDIA not in contenu:
    erreurs.append("bloc media query introuvable tel quel")
else:
    contenu = contenu.replace(ANCIEN_MEDIA, NOUVEAU_MEDIA)
    remplacements_ok += 1

# ------------------------------------------------------------------
# 3) JS qui construit l'accordeon (nouveau script independant, ne
#    touche pas au guide vocal existant)
# ------------------------------------------------------------------
ANCIEN_SCRIPT_ANCRE = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js"></script>'''

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

    // Ecouteur separe de celui du guide vocal : les deux coexistent.
    titre.addEventListener('click', function () {
      panel.classList.toggle('is-collapsed');
    });
  });
});
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js"></script>'''

if 'Regroupe tout le contenu du panneau' in contenu:
    pass
elif ANCIEN_SCRIPT_ANCRE not in contenu:
    erreurs.append("ancre des balises leaflet.js introuvable")
else:
    contenu = contenu.replace(ANCIEN_SCRIPT_ANCRE, NOUVEAU_SCRIPT, 1)
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