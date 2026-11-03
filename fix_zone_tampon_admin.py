# -*- coding: utf-8 -*-
"""
Ajoute la zone tampon (meme principe que le geoportail public) au
geoportail admin : un bouton "Choisir un point sur la carte" dans le
panneau "Rayon de couverture", qui dessine un cercle et reutilise le
moteur de selection spatiale deja present (calculerSelection) pour
lister les parcelles concernees.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "btnRayonPointLibre"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) HTML : bouton "Choisir un point sur la carte" ---
    ancien_html = '''        <label class="geo-field-label" for="rayon-infra-select">Centrer sur une infrastructure</label>
        <select id="rayon-infra-select" class="geo-field-select">
          <option value="">Choisir une infrastructure...</option>
        </select>
        <label class="geo-field-label">Rayon</label>'''
    if ancien_html not in contenu:
        raise SystemExit("ANCRE HTML panneau rayon INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_html = '''        <label class="geo-field-label" for="rayon-infra-select">Centrer sur une infrastructure</label>
        <select id="rayon-infra-select" class="geo-field-select">
          <option value="">Choisir une infrastructure...</option>
        </select>
        <button type="button" id="btnRayonPointLibre" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:8px; margin-bottom:8px;">
          <i class="fa-solid fa-map-pin"></i> Choisir un point sur la carte
        </button>
        <label class="geo-field-label">Rayon</label>'''
    contenu = contenu.replace(ancien_html, nouveau_html)

    # --- 2) Variables globales modeChoixRayon / formeSelectionActuelle ---
    ancienne_var = "let coucheRayon = null;"
    if ancienne_var not in contenu:
        raise SystemExit("ANCRE 'let coucheRayon' INTROUVABLE - abandon partiel, verifie le fichier.")
    nouvelle_var = ancienne_var + "\nlet modeChoixRayon = false;\nlet formeSelectionRayon = null;"
    contenu = contenu.replace(ancienne_var, nouvelle_var)

    # --- 3) Remplacement complet de mettreAJourRayon + nouvelle fonction partagee ---
    ancienne_fonction = '''  function mettreAJourRayon() {
    const select = document.getElementById('rayon-infra-select');
    const opt = select.options[select.selectedIndex];
    const result = document.getElementById('rayon-result');
    if (coucheRayon) { map.removeLayer(coucheRayon); coucheRayon = null; }
    if (!opt || !opt.value) { if (result) result.textContent = ''; return; }

    const lat = parseFloat(opt.dataset.lat);
    const lng = parseFloat(opt.dataset.lng);
    const rayon = parseInt(document.getElementById('rayon-slider').value, 10);
    const centre = L.latLng(lat, lng);

    coucheRayon = L.circle(centre, { radius: rayon, color: '#b23b2e', weight: 2.5, fillColor: '#b23b2e', fillOpacity: 0.15 }).addTo(map);
    map.flyTo(centre, 15);

    let compte = 0;
    (allParcelles.features || []).forEach(function (f) {
      if (!f.geometry) return;
      const centreParcelle = L.geoJSON(f).getBounds().getCenter();
      if (centre.distanceTo(centreParcelle) <= rayon) compte++;
    });
    if (result) result.innerHTML = '<span style="color:#2f7a4f;"><i class="fa-solid fa-circle-check"></i> ' + compte + ' parcelle' + (compte > 1 ? 's' : '') + ' dans ce rayon</span>';
  }'''
    if ancienne_fonction not in contenu:
        raise SystemExit("ANCRE mettreAJourRayon INTROUVABLE - abandon partiel, verifie le fichier.")

    nouvelle_fonction = '''  function calculerRayonAutour(centre, rayon) {
    if (coucheRayon) { map.removeLayer(coucheRayon); coucheRayon = null; }
    const result = document.getElementById('rayon-result');

    coucheRayon = L.circle(centre, { radius: rayon, color: '#b23b2e', weight: 2.5, fillColor: '#b23b2e', fillOpacity: 0.15 }).addTo(map);
    map.flyTo(centre, 15);

    if (typeof turf !== 'undefined') {
      const forme = turf.circle([centre.lng, centre.lat], rayon / 1000, { steps: 64, units: 'kilometers' });
      formeSelectionRayon = forme;
      if (coucheFormeSelection) { map.removeLayer(coucheFormeSelection); coucheFormeSelection = null; }
      calculerSelection(forme);
      if (result) {
        result.innerHTML = '<span style="color:#2f7a4f;"><i class="fa-solid fa-circle-check"></i> Zone de ' + rayon + ' m calculée. Voir le détail dans le panneau « Sélection spatiale » ci-dessous.</span>';
      }
    } else if (result) {
      result.innerHTML = '<span style="color:#b23b2e;">Turf.js indisponible.</span>';
    }
  }

  function mettreAJourRayon() {
    const select = document.getElementById('rayon-infra-select');
    const opt = select.options[select.selectedIndex];
    const result = document.getElementById('rayon-result');
    if (!opt || !opt.value) {
      if (coucheRayon) { map.removeLayer(coucheRayon); coucheRayon = null; }
      if (result) result.textContent = '';
      return;
    }

    const lat = parseFloat(opt.dataset.lat);
    const lng = parseFloat(opt.dataset.lng);
    const rayon = parseInt(document.getElementById('rayon-slider').value, 10);
    calculerRayonAutour(L.latLng(lat, lng), rayon);
  }'''
    contenu = contenu.replace(ancienne_fonction, nouvelle_fonction)

    # --- 4) Branche "point libre" dans le clic carte + branchement du bouton ---
    ancien_click = '''    map.on('click', function (e) {
      if (!modeMesure) return;
      pointsMesure.push(e.latlng);
      redessinerMesure();
    });

    Promise.all([loadZones(), loadParcelles(), loadSections(), loadLimites()]).finally(function () {'''
    if ancien_click not in contenu:
        raise SystemExit("ANCRE map.on('click') (admin) INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_click = '''    map.on('click', function (e) {
      if (modeChoixRayon) {
        modeChoixRayon = false;
        const conteneurCarteR = document.getElementById('map');
        if (conteneurCarteR) conteneurCarteR.style.cursor = '';
        const btnRayon = document.getElementById('btnRayonPointLibre');
        if (btnRayon) btnRayon.innerHTML = '<i class="fa-solid fa-map-pin"></i> Choisir un point sur la carte';
        const selectInfra = document.getElementById('rayon-infra-select');
        if (selectInfra) selectInfra.value = '';
        const rayon = parseInt(document.getElementById('rayon-slider').value, 10);
        calculerRayonAutour(e.latlng, rayon);
        return;
      }
      if (!modeMesure) return;
      pointsMesure.push(e.latlng);
      redessinerMesure();
    });

    const btnRayonPointLibre = document.getElementById('btnRayonPointLibre');
    if (btnRayonPointLibre) {
      btnRayonPointLibre.addEventListener('click', function () {
        modeChoixRayon = true;
        const conteneurCarte = document.getElementById('map');
        if (conteneurCarte) conteneurCarte.style.cursor = 'crosshair';
        btnRayonPointLibre.innerHTML = '<i class="fa-solid fa-crosshairs"></i> Clique sur la carte pour choisir...';
      });
    }

    Promise.all([loadZones(), loadParcelles(), loadSections(), loadLimites()]).finally(function () {'''
    contenu = contenu.replace(ancien_click, nouveau_click)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")