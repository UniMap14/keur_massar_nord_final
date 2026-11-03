# -*- coding: utf-8 -*-
"""
Ajoute un panneau "Pression fonciere" au geoportail ADMIN uniquement
(jamais au public) avec 3 analyses :
  1) Taux de bati par quartier (classement).
  2) Parcelles non baties situees pres des infrastructures (seuil
     configurable), listees par distance croissante.
  3) Parcelles sans titre foncier, regroupees par quartier.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "btnAnalyserBati"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) HTML : nouveau panneau, juste apres "Statistiques par quartier" ---
    ancien_html = '''        <label class="geo-layer-item" style="margin-top:10px;">
          <input type="checkbox" id="toggle-choropleth">
          <span>Carte de pression foncière (densité de parcelles)</span>
        </label>
      </div>

      <!-- ===== NOUVEAU : Comparaison des quartiers ===== -->'''
    if ancien_html not in contenu:
        raise SystemExit("ANCRE HTML (fin panneau Statistiques par quartier) INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_html = '''        <label class="geo-layer-item" style="margin-top:10px;">
          <input type="checkbox" id="toggle-choropleth">
          <span>Carte de pression foncière (densité de parcelles)</span>
        </label>
      </div>

      <!-- ===== NOUVEAU : Pression fonciere (admin uniquement) ===== -->
      <div class="geo-panel">
        <h2 class="geo-panel-title" data-collapsed="true"><i class="fa-solid fa-chart-pie"></i> Pression foncière <em style="font-weight:400; color:var(--geo-texte-mute);">(admin)</em></h2>

        <label class="geo-field-label" style="margin-top:0;">Taux de bâti par quartier</label>
        <button type="button" id="btnAnalyserBati" class="geo-btn geo-btn-primary geo-btn-block">
          <i class="fa-solid fa-chart-column"></i> Analyser
        </button>
        <div id="batiResult" class="geo-tool-result"></div>

        <label class="geo-field-label" style="margin-top:14px;">Parcelles non bâties près des infrastructures</label>
        <select id="seuil-non-bati" class="geo-field-select">
          <option value="300">300 m</option>
          <option value="500" selected>500 m</option>
          <option value="1000">1 km</option>
        </select>
        <button type="button" id="btnAnalyserNonBati" class="geo-btn geo-btn-primary geo-btn-block" style="margin-top:8px;">
          <i class="fa-solid fa-magnifying-glass-chart"></i> Analyser
        </button>
        <div id="nonBatiResult" class="geo-tool-result"></div>

        <label class="geo-field-label" style="margin-top:14px;">Parcelles sans titre foncier</label>
        <button type="button" id="btnAnalyserSansTitre" class="geo-btn geo-btn-primary geo-btn-block">
          <i class="fa-solid fa-file-circle-exclamation"></i> Analyser
        </button>
        <div id="sansTitreResult" class="geo-tool-result"></div>
      </div>

      <!-- ===== NOUVEAU : Comparaison des quartiers ===== -->'''
    contenu = contenu.replace(ancien_html, nouveau_html)

    # --- 2) JS : nouvelles fonctions, juste apres calculerStatsQuartiers() ---
    ancien_js = '''    statsParQuartier.sort(function (a, b) { return b.nbParcelles - a.nbParcelles; });
    maxDensiteQuartiers = statsParQuartier.reduce(function (m, s) { return Math.max(m, s.densite); }, 0);
  }'''
    if ancien_js not in contenu:
        raise SystemExit("ANCRE fin calculerStatsQuartiers INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_js = '''    statsParQuartier.sort(function (a, b) { return b.nbParcelles - a.nbParcelles; });
    maxDensiteQuartiers = statsParQuartier.reduce(function (m, s) { return Math.max(m, s.densite); }, 0);
  }

  // ===== NOUVEAU : Pression fonciere (admin uniquement) =====
  function estBati(occ) {
    const o = (occ || '').toLowerCase();
    return o.indexOf('bati') !== -1 || o.indexOf('b\\u00e2ti') !== -1;
  }

  function analyserTauxBati() {
    const resultEl = document.getElementById('batiResult');
    if (!statsParQuartier.length) calculerStatsQuartiers();

    const lignes = (allZones.features || []).map(function (zoneFeature) {
      const nom = nomZone(zoneFeature);
      const parcellesDuQuartier = parcellesParZone[nom] || [];
      const total = parcellesDuQuartier.length;
      let batiCount = 0;
      parcellesDuQuartier.forEach(function (f) { if (estBati(f.properties.occupation_sol)) batiCount++; });
      const taux = total > 0 ? Math.round((batiCount / total) * 100) : 0;
      return { nom: nom, total: total, batiCount: batiCount, taux: taux };
    }).filter(function (l) { return l.total > 0; });

    lignes.sort(function (a, b) { return b.taux - a.taux; });

    if (!lignes.length) {
      resultEl.innerHTML = '<span style="color:#b23b2e;">Aucune donn\\u00e9e disponible.</span>';
      return;
    }

    resultEl.innerHTML = '<div class="geo-selection-liste">' +
      lignes.map(function (l) {
        return '<div class="geo-selection-item" data-zone="' + echapperHtml(l.nom) + '"><span class="nom">' + echapperHtml(l.nom) + '</span><span class="val">' + l.taux + '% b\\u00e2ti (' + l.batiCount + '/' + l.total + ')</span></div>';
      }).join('') + '</div>';

    resultEl.querySelectorAll('.geo-selection-item').forEach(function (el) {
      el.style.cursor = 'pointer';
      el.addEventListener('click', function () { selectionnerQuartier(el.getAttribute('data-zone')); });
    });
  }

  function analyserNonBatiProches() {
    const resultEl = document.getElementById('nonBatiResult');
    const seuil = parseInt(document.getElementById('seuil-non-bati').value, 10);

    const infras = (typeof infrastructuresFiltrees === 'function')
      ? infrastructuresFiltrees({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle })
      : toutesLesInfrastructures({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle }).filter(function (i) { return i.latitude != null && i.longitude != null; });

    if (!infras.length) {
      resultEl.innerHTML = '<span style="color:#b23b2e;">Aucune infrastructure \\u00e0 analyser.</span>';
      return;
    }

    resultEl.textContent = 'Calcul en cours...';

    setTimeout(function () {
      const nonBaties = (allParcelles.features || []).filter(function (f) {
        return f.geometry && !estBati(f.properties.occupation_sol);
      });

      const resultats = [];
      nonBaties.forEach(function (f) {
        let centre;
        try { centre = turf.centroid(f).geometry.coordinates; } catch (e) { return; }
        const point = L.latLng(centre[1], centre[0]);
        let distMin = Infinity;
        for (let i = 0; i < infras.length; i++) {
          const d = point.distanceTo(L.latLng(infras[i].latitude, infras[i].longitude));
          if (d < distMin) distMin = d;
        }
        if (distMin <= seuil) resultats.push({ f: f, distance: distMin });
      });

      resultats.sort(function (a, b) { return a.distance - b.distance; });

      if (!resultats.length) {
        resultEl.innerHTML = '<span style="color:#766c5d;">Aucune parcelle non b\\u00e2tie \\u00e0 moins de ' + seuil + ' m d\\'une infrastructure.</span>';
        return;
      }

      const LIMITE = 30;
      let html = '<div style="font-size:12px; color:#766c5d; margin-bottom:6px;">' + resultats.length + ' parcelle(s) non b\\u00e2tie(s) \\u00e0 moins de ' + seuil + ' m</div>';
      html += '<div class="geo-selection-liste">' + resultats.slice(0, LIMITE).map(function (r) {
        const p = r.f.properties;
        const distTxt = r.distance >= 1000 ? (r.distance / 1000).toFixed(1) + ' km' : Math.round(r.distance) + ' m';
        return '<div class="geo-selection-item" data-nicad="' + echapperHtml(p.nicad) + '"><span class="nom">' + echapperHtml(p.nicad || '\\u2014') + '</span><span class="val">' + distTxt + '</span></div>';
      }).join('') + '</div>';
      if (resultats.length > LIMITE) {
        html += '<div class="geo-selection-plus">+ ' + (resultats.length - LIMITE) + ' autres</div>';
      }
      resultEl.innerHTML = html;

      resultEl.querySelectorAll('.geo-selection-item').forEach(function (el) {
        el.addEventListener('click', function () {
          const nicad = el.getAttribute('data-nicad');
          const trouve = resultats.find(function (r) { return r.f.properties.nicad === nicad; });
          if (trouve) {
            map.fitBounds(L.geoJSON(trouve.f).getBounds(), { padding: [60, 60], maxZoom: 19 });
          }
        });
      });
    }, 50);
  }

  function analyserSansTitre() {
    const resultEl = document.getElementById('sansTitreResult');

    const sansTitre = (allParcelles.features || []).filter(function (f) {
      return !f.properties.numero_titre_foncier;
    });

    if (!sansTitre.length) {
      resultEl.innerHTML = '<span style="color:#2f7a4f;">Toutes les parcelles ont un titre foncier renseign\\u00e9.</span>';
      return;
    }

    const comptesParZone = {};
    sansTitre.forEach(function (f) {
      const nom = f.properties.zone_nom || 'Zone inconnue';
      comptesParZone[nom] = (comptesParZone[nom] || 0) + 1;
    });

    const zonesTriees = Object.keys(comptesParZone).sort(function (a, b) { return comptesParZone[b] - comptesParZone[a]; });

    let html = '<div style="font-size:12px; color:#766c5d; margin-bottom:6px;">' + sansTitre.length + ' parcelle(s) sans titre foncier</div>';
    html += '<div class="geo-selection-liste">' + zonesTriees.map(function (nom) {
      return '<div class="geo-selection-item" data-zone="' + echapperHtml(nom) + '"><span class="nom">' + echapperHtml(nom) + '</span><span class="val">' + comptesParZone[nom] + '</span></div>';
    }).join('') + '</div>';
    resultEl.innerHTML = html;

    resultEl.querySelectorAll('.geo-selection-item').forEach(function (el) {
      el.style.cursor = 'pointer';
      el.addEventListener('click', function () { selectionnerQuartier(el.getAttribute('data-zone')); });
    });
  }'''
    contenu = contenu.replace(ancien_js, nouveau_js)

    # --- 3) Branchement des 3 boutons ---
    ancien_wiring = "    onEvent('toggle-choropleth', 'change', function (e) { basculerChoropleth(e.target.checked); });"
    if ancien_wiring not in contenu:
        raise SystemExit("ANCRE onEvent toggle-choropleth INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_wiring = ancien_wiring + '''
    onEvent('btnAnalyserBati', 'click', analyserTauxBati);
    onEvent('btnAnalyserNonBati', 'click', analyserNonBatiProches);
    onEvent('btnAnalyserSansTitre', 'click', analyserSansTitre);'''
    contenu = contenu.replace(ancien_wiring, nouveau_wiring)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")