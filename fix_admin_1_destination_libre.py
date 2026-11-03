# -*- coding: utf-8 -*-
"""
ADMIN - Feature 1/6 : Choisir une destination sur la carte (itineraire libre),
en reprenant la fonction calculerItineraire() deja presente dans admin.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "btnChoisirDestination"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) HTML : bouton dans le panneau Itineraire, apres position-status ---
    ancien_html = '''        <button id="btnGeolocaliser" class="geo-btn geo-btn-ghost geo-btn-block">
          <i class="fa-solid fa-location-dot"></i> Me géolocaliser
        </button>
        <div id="position-status" style="margin-top:8px; font-size:12px;" aria-live="polite"></div>'''
    if ancien_html not in contenu:
        raise SystemExit("ANCRE HTML (bouton Me geolocaliser) INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_html = '''        <button id="btnGeolocaliser" class="geo-btn geo-btn-ghost geo-btn-block">
          <i class="fa-solid fa-location-dot"></i> Me géolocaliser
        </button>
        <div id="position-status" style="margin-top:8px; font-size:12px;" aria-live="polite"></div>

        <button type="button" id="btnChoisirDestination" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:8px;">
          <i class="fa-solid fa-map-pin"></i> Choisir une destination sur la carte
        </button>'''
    contenu = contenu.replace(ancien_html, nouveau_html)

    # --- 2) JS : variable d'etat modeChoixDestination, pres de modeChoixRayon ---
    ancien_var = "let modeChoixRayon = false;\nlet formeSelectionRayon = null;"
    if ancien_var not in contenu:
        raise SystemExit("ANCRE variable modeChoixRayon INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_var = ancien_var + "\nlet modeChoixDestination = false;"
    contenu = contenu.replace(ancien_var, nouveau_var)

    # --- 3) JS : branche dans map.on('click', ...) + wiring du bouton ---
    ancien_click = '''    map.on('click', function (e) {
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
    }'''
    if ancien_click not in contenu:
        raise SystemExit("ANCRE map.on('click') INTROUVABLE - abandon partiel, verifie le fichier.")

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
      if (modeChoixDestination) {
        modeChoixDestination = false;
        const conteneurCarteD = document.getElementById('map');
        if (conteneurCarteD) conteneurCarteD.style.cursor = '';
        const btnDest = document.getElementById('btnChoisirDestination');
        if (btnDest) btnDest.innerHTML = '<i class="fa-solid fa-map-pin"></i> Choisir une destination sur la carte';
        calculerItineraire(e.latlng.lat, e.latlng.lng);
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

    const btnChoisirDestination = document.getElementById('btnChoisirDestination');
    if (btnChoisirDestination) {
      btnChoisirDestination.addEventListener('click', function () {
        modeChoixDestination = true;
        const conteneurCarteD2 = document.getElementById('map');
        if (conteneurCarteD2) conteneurCarteD2.style.cursor = 'crosshair';
        btnChoisirDestination.innerHTML = '<i class="fa-solid fa-crosshairs"></i> Clique sur la carte...';
      });
    }'''
    contenu = contenu.replace(ancien_click, nouveau_click)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes (feature 1/6 : destination libre).")