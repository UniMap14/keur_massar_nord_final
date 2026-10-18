# -*- coding: utf-8 -*-
"""
Ajoute un filtre d'affichage Parcelles / Infrastructures / Les deux
sur foncier/templates/foncier/geoportail_admin.html, avec desactivation
automatique des outils qui dependent de la couche masquee.
Idempotent : si un patch est deja applique, le script le signale et ne
touche a rien.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/foncier/geoportail_admin.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) CSS : regle pour les controles desactives
# ---------------------------------------------------------------------
ANCRE_CSS = "  .geo-layer-item input { accent-color: var(--geo-vert); width: 15px; height: 15px; }\n"
AJOUT_CSS = "  .geo-disabled { opacity: 0.4 !important; pointer-events: none !important; cursor: not-allowed !important; }\n"
if "geo-disabled" in texte:
    pass  # deja applique
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, ANCRE_CSS + AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# 2) HTML : remplace la case "Parcelles" par le controle 3 boutons
# ---------------------------------------------------------------------
ANCRE_HTML = '''      <div class="geo-panel">
        <h2 class="geo-panel-title"><i class="fa-solid fa-layer-group"></i> Couches SIG</h2>
        <div class="geo-layer-list">
          <label class="geo-layer-item"><input type="checkbox" id="toggle-zones" checked><span>Zones/Quartiers</span></label>
          <label class="geo-layer-item"><input type="checkbox" id="toggle-parcelles" checked><span>Parcelles</span></label>
          <label class="geo-layer-item"><input type="checkbox" id="toggle-sections"><span>Sections cadastrales</span></label>
          <label class="geo-layer-item"><input type="checkbox" id="toggle-limites" checked><span>Limites administratives</span></label>
        </div>
      </div>'''
NOUVEAU_HTML = '''      <div class="geo-panel">
        <h2 class="geo-panel-title"><i class="fa-solid fa-layer-group"></i> Couches SIG</h2>
        <label class="geo-field-label" style="margin-top:0;">Affichage</label>
        <div class="geo-tab-bar" id="modeAffichageBar" style="margin-bottom:10px;">
          <button type="button" class="geo-tab-btn" data-mode="PARCELLES">Parcelles</button>
          <button type="button" class="geo-tab-btn" data-mode="INFRA">Infrastructures</button>
          <button type="button" class="geo-tab-btn active" data-mode="TOUS">Les deux</button>
        </div>
        <div class="geo-layer-list">
          <label class="geo-layer-item"><input type="checkbox" id="toggle-zones" checked><span>Zones/Quartiers</span></label>
          <label class="geo-layer-item"><input type="checkbox" id="toggle-sections"><span>Sections cadastrales</span></label>
          <label class="geo-layer-item"><input type="checkbox" id="toggle-limites" checked><span>Limites administratives</span></label>
        </div>
      </div>'''
if "modeAffichageBar" in texte:
    pass  # deja applique
elif ANCRE_HTML not in texte:
    erreurs.append("ANCRE_HTML introuvable")
else:
    texte = texte.replace(ANCRE_HTML, NOUVEAU_HTML, 1)

# ---------------------------------------------------------------------
# 3) JS : declaration de infrastructuresVisible / modeAffichage
# ---------------------------------------------------------------------
ANCRE_DECL = "  let zonesVisible = true, parcellesVisible = true, sectionsVisible = false, limitesVisible = true;\n"
AJOUT_DECL = "  let infrastructuresVisible = true;\n  let modeAffichage = 'TOUS';\n"
if "let infrastructuresVisible" in texte:
    pass
elif ANCRE_DECL not in texte:
    erreurs.append("ANCRE_DECL introuvable")
else:
    texte = texte.replace(ANCRE_DECL, ANCRE_DECL + AJOUT_DECL, 1)

# ---------------------------------------------------------------------
# 4) JS : afficherIconesInfrastructures respecte infrastructuresVisible
# ---------------------------------------------------------------------
ANCRE_INFRA = """    if (modeChaleurActif) {
      afficherGrilleDensite(infrasAffichees);
    } else {
      coucheInfrastructures.addTo(map);
    }
  }"""
NOUVEAU_INFRA = """    if (!infrastructuresVisible) {
      // Couche masquee : rien a afficher
    } else if (modeChaleurActif) {
      afficherGrilleDensite(infrasAffichees);
    } else {
      coucheInfrastructures.addTo(map);
    }
  }"""
if "// Couche masquee : rien a afficher" in texte:
    pass
elif ANCRE_INFRA not in texte:
    erreurs.append("ANCRE_INFRA introuvable")
else:
    texte = texte.replace(ANCRE_INFRA, NOUVEAU_INFRA, 1)

# ---------------------------------------------------------------------
# 5) JS : mettreAJourStats affiche "-" pour la couche masquee
# ---------------------------------------------------------------------
ANCRE_STATS = """  function mettreAJourStats(features) {
    const elParcelles = document.getElementById('statParcelles');
    if (elParcelles) elParcelles.textContent = features.length.toLocaleString('fr-FR');

    let superficieTotale = 0;
    features.forEach(function (f) { superficieTotale += (f.properties.superficie || 0); });
    const elSuperficie = document.getElementById('statSuperficie');
    if (elSuperficie) {
      elSuperficie.textContent = superficieTotale >= 10000
        ? (superficieTotale / 10000).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' ha'
        : Math.round(superficieTotale).toLocaleString('fr-FR') + ' m²';
    }

    let totalInfra = infraSansParcelle.length;
    features.forEach(function (f) { totalInfra += (f.properties.infrastructures || []).length; });
    const elInfra = document.getElementById('statInfra');
    if (elInfra) elInfra.textContent = totalInfra.toLocaleString('fr-FR');
  }"""
NOUVEAU_STATS = """  function mettreAJourStats(features) {
    const elParcelles = document.getElementById('statParcelles');
    if (elParcelles) elParcelles.textContent = parcellesVisible ? features.length.toLocaleString('fr-FR') : '—';

    let superficieTotale = 0;
    features.forEach(function (f) { superficieTotale += (f.properties.superficie || 0); });
    const elSuperficie = document.getElementById('statSuperficie');
    if (elSuperficie) {
      elSuperficie.textContent = !parcellesVisible ? '—' : (superficieTotale >= 10000
        ? (superficieTotale / 10000).toLocaleString('fr-FR', { maximumFractionDigits: 1 }) + ' ha'
        : Math.round(superficieTotale).toLocaleString('fr-FR') + ' m²');
    }

    let totalInfra = infraSansParcelle.length;
    features.forEach(function (f) { totalInfra += (f.properties.infrastructures || []).length; });
    const elInfra = document.getElementById('statInfra');
    if (elInfra) elInfra.textContent = infrastructuresVisible ? totalInfra.toLocaleString('fr-FR') : '—';
  }"""
if "parcellesVisible ? features.length" in texte:
    pass
elif ANCRE_STATS not in texte:
    erreurs.append("ANCRE_STATS introuvable")
else:
    texte = texte.replace(ANCRE_STATS, NOUVEAU_STATS, 1)

# ---------------------------------------------------------------------
# 6) JS : tableau des parcelles -> message si couche masquee
# ---------------------------------------------------------------------
ANCRE_TABLE = """  function remplirTableauParcelles(features) {
    const corps = document.getElementById('dataTableAdminBody');
    const meta = document.getElementById('tableMetaAdmin');
    if (!corps) return;
"""
NOUVEAU_TABLE = """  function remplirTableauParcelles(features) {
    const corps = document.getElementById('dataTableAdminBody');
    const meta = document.getElementById('tableMetaAdmin');
    if (!corps) return;

    if (!parcellesVisible) {
      const nbColonnesMasque = peutFiscal ? 5 : 3;
      meta.textContent = 'Couche masquée';
      corps.innerHTML = '<tr><td colspan="' + nbColonnesMasque + '" class="table-empty">Activez la couche « Parcelles » (panneau Couches SIG) pour afficher ce tableau.</td></tr>';
      return;
    }
"""
if "Couche masquée" in texte:
    pass
elif ANCRE_TABLE not in texte:
    erreurs.append("ANCRE_TABLE introuvable")
else:
    texte = texte.replace(ANCRE_TABLE, NOUVEAU_TABLE, 1)

# ---------------------------------------------------------------------
# 7) JS : fonctions de disponibilite des outils + bascule de mode
# ---------------------------------------------------------------------
ANCRE_AVANT_EVENEMENTS = """  document.addEventListener('DOMContentLoaded', function () {
    function onEvent(id, evenement, gestionnaire) {
      const el = document.getElementById(id);
      if (el) el.addEventListener(evenement, gestionnaire);
      else console.warn('Élément #' + id + ' introuvable (ignoré).');
    }

    onEvent('btnGeolocaliser', 'click', localiserMoi);"""
AJOUT_FONCTIONS = """  const OUTILS_PARCELLES = ['search-nicad', 'btnSearchParcelle', 'filter-occupation', 'filter-statut', 'quartier-select', 'toggle-choropleth', 'btnDessinPolygone', 'btnDessinRectangle', 'btnDessinCercle', 'btnExportCSV', 'btnExportGeoJSON'];
  const OUTILS_INFRA = ['search-infra', 'btnSearchInfra', 'filter-infra-categorie', 'toggle-carte-chaleur', 'rayon-infra-select', 'rayon-slider', 'seuil-desserte', 'btnAnalyserDesserte', 'toggle-voronoi'];

  function definirDisponibilite(ids, actif) {
    ids.forEach(function (id) {
      const el = document.getElementById(id);
      if (!el) return;
      el.disabled = !actif;
      el.title = actif ? '' : "Indisponible : activez d'abord la couche correspondante dans « Couches SIG ».";
      const conteneur = el.closest('.geo-layer-item') || el;
      conteneur.classList.toggle('geo-disabled', !actif);
    });
  }

  function appliquerDisponibiliteOutils() {
    definirDisponibilite(OUTILS_PARCELLES, parcellesVisible);
    definirDisponibilite(OUTILS_INFRA, infrastructuresVisible);

    if (!parcellesVisible) {
      effacerSelection();
      const choroBox = document.getElementById('toggle-choropleth');
      if (choroBox && choroBox.checked) { choroBox.checked = false; basculerChoropleth(false); }
    }
    if (!infrastructuresVisible) {
      const voronoiBox = document.getElementById('toggle-voronoi');
      if (voronoiBox && voronoiBox.checked) { voronoiBox.checked = false; basculerVoronoi(false); }
      const chaleurBox = document.getElementById('toggle-carte-chaleur');
      if (chaleurBox && chaleurBox.checked) { chaleurBox.checked = false; basculerCarteChaleur(false); }
    }
  }

  function definirModeAffichage(mode) {
    modeAffichage = mode;
    parcellesVisible = (mode !== 'INFRA');
    infrastructuresVisible = (mode !== 'PARCELLES');
    const barre = document.getElementById('modeAffichageBar');
    if (barre) {
      barre.querySelectorAll('.geo-tab-btn').forEach(function (btn) {
        btn.classList.toggle('active', btn.dataset.mode === mode);
      });
    }
    appliquerDisponibiliteOutils();
    redessinerCouches();
    afficherIconesInfrastructures(dernieresDonneesInfra || allParcelles);
  }

  document.addEventListener('DOMContentLoaded', function () {
    function onEvent(id, evenement, gestionnaire) {
      const el = document.getElementById(id);
      if (el) el.addEventListener(evenement, gestionnaire);
      else console.warn('Élément #' + id + ' introuvable (ignoré).');
    }

    onEvent('btnGeolocaliser', 'click', localiserMoi);"""
if "function definirModeAffichage" in texte:
    pass
elif ANCRE_AVANT_EVENEMENTS not in texte:
    erreurs.append("ANCRE_AVANT_EVENEMENTS introuvable")
else:
    texte = texte.replace(ANCRE_AVANT_EVENEMENTS, AJOUT_FONCTIONS, 1)

# ---------------------------------------------------------------------
# 8) JS : remplace l'ecouteur toggle-parcelles par le branchement des boutons
# ---------------------------------------------------------------------
ANCRE_EVT = """    onEvent('toggle-zones', 'change', function (e) { zonesVisible = e.target.checked; redessinerCouches(); });
    onEvent('toggle-parcelles', 'change', function (e) { parcellesVisible = e.target.checked; redessinerCouches(); });
    onEvent('toggle-sections', 'change', function (e) { sectionsVisible = e.target.checked; redessinerCouches(); });"""
NOUVEAU_EVT = """    onEvent('toggle-zones', 'change', function (e) { zonesVisible = e.target.checked; redessinerCouches(); });
    document.querySelectorAll('#modeAffichageBar .geo-tab-btn').forEach(function (btn) {
      btn.addEventListener('click', function () { definirModeAffichage(btn.dataset.mode); });
    });
    appliquerDisponibiliteOutils();
    onEvent('toggle-sections', 'change', function (e) { sectionsVisible = e.target.checked; redessinerCouches(); });"""
if "definirModeAffichage(btn.dataset.mode)" in texte:
    pass
elif ANCRE_EVT not in texte:
    erreurs.append("ANCRE_EVT introuvable")
else:
    texte = texte.replace(ANCRE_EVT, NOUVEAU_EVT, 1)

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
    print("OK : geoportail_admin.html mis a jour.")