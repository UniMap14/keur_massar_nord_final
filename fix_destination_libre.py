# -*- coding: utf-8 -*-
"""
Ajoute un bouton "Choisir une destination sur la carte" dans le panneau
Itineraire du geoportail public. Une fois active, le prochain clic sur
la carte devient la destination et declenche le calcul multi-modal
(a pied / velo / moto / voiture) deja existant via calculerItineraire.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "btnChoisirDestination"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Bouton dans le panneau HTML, juste apres le statut de position ---
    ancien_html = '''        <div id="position-status" style="margin-top:8px; font-size:12px;" aria-live="polite"></div>

        <div id="proximite-section" style="margin-top:12px; display:none;">'''
    if ancien_html not in contenu:
        raise SystemExit("ANCRE HTML (position-status) INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_html = '''        <div id="position-status" style="margin-top:8px; font-size:12px;" aria-live="polite"></div>

        <button type="button" id="btnChoisirDestination" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:8px;">
          <i class="fa-solid fa-map-pin"></i> Choisir une destination sur la carte
        </button>

        <div id="proximite-section" style="margin-top:12px; display:none;">'''
    contenu = contenu.replace(ancien_html, nouveau_html)

    # --- 2) Titre generique du panneau resultat (plus seulement "la parcelle") ---
    ancien_titre = '''<div style="font-size:11px; color:#766c5d; margin-bottom:6px;">Depuis votre position jusqu'a la parcelle</div>'''
    if ancien_titre not in contenu:
        raise SystemExit("ANCRE titre route-info INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_titre = '''<div id="route-info-titre" style="font-size:11px; color:#766c5d; margin-bottom:6px;">Depuis votre position jusqu'a la destination choisie</div>'''
    contenu = contenu.replace(ancien_titre, nouveau_titre)

    # --- 3) Variable d'etat JS, a cote de userLatLng ---
    ancienne_var = "let userLatLng = null;"
    if ancienne_var not in contenu:
        raise SystemExit("ANCRE 'userLatLng' INTROUVABLE - abandon partiel, verifie le fichier.")
    nouvelle_var = ancienne_var + "\n  let modeChoixDestination = false;"
    contenu = contenu.replace(ancienne_var, nouvelle_var)

    # --- 4) Gestionnaire de clic carte : brancher le mode destination AVANT le mode mesure ---
    ancien_click = '''    map.on('click', function (e) {
      if (!modeMesure) return;
      pointsMesure.push(e.latlng);
      redessinerMesure();
    });'''
    if ancien_click not in contenu:
        raise SystemExit("ANCRE map.on('click') INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_click = '''    map.on('click', function (e) {
      if (modeChoixDestination) {
        modeChoixDestination = false;
        const conteneurCarte = document.getElementById('map');
        if (conteneurCarte) conteneurCarte.style.cursor = '';
        const btnDest = document.getElementById('btnChoisirDestination');
        if (btnDest) btnDest.innerHTML = '<i class="fa-solid fa-map-pin"></i> Choisir une destination sur la carte';
        calculerItineraire(e.latlng.lat, e.latlng.lng);
        return;
      }
      if (!modeMesure) return;
      pointsMesure.push(e.latlng);
      redessinerMesure();
    });

    const btnChoisirDestination = document.getElementById('btnChoisirDestination');
    if (btnChoisirDestination) {
      btnChoisirDestination.addEventListener('click', function () {
        if (!userLatLng) {
          const status = document.getElementById('position-status');
          if (status) status.innerHTML = '<span style="color:#dc3545;"><i class="fa-solid fa-triangle-exclamation"></i> Clique d\\'abord sur \\u00ab Me g\\u00e9olocaliser \\u00bb.</span>';
          return;
        }
        modeChoixDestination = true;
        const conteneurCarte = document.getElementById('map');
        if (conteneurCarte) conteneurCarte.style.cursor = 'crosshair';
        btnChoisirDestination.innerHTML = '<i class="fa-solid fa-crosshairs"></i> Clique sur la carte pour choisir...';
      });
    }'''
    contenu = contenu.replace(ancien_click, nouveau_click)

    # --- 5) Depuis la liste "infrastructures les plus proches" : clic = calcul itineraire aussi ---
    ancien_infra_click = '''      liste.querySelectorAll('.geo-proximite-item').forEach(function (el) {
        el.style.cursor = 'pointer';
        el.addEventListener('click', function () {
          const lat = parseFloat(el.getAttribute('data-lat'));
          const lng = parseFloat(el.getAttribute('data-lng'));
          map.flyTo([lat, lng], 17);
        });
      });'''
    if ancien_infra_click not in contenu:
        raise SystemExit("ANCRE liste infrastructures INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_infra_click = '''      liste.querySelectorAll('.geo-proximite-item').forEach(function (el) {
        el.style.cursor = 'pointer';
        el.addEventListener('click', function () {
          const lat = parseFloat(el.getAttribute('data-lat'));
          const lng = parseFloat(el.getAttribute('data-lng'));
          map.flyTo([lat, lng], 17);
          if (userLatLng) calculerItineraire(lat, lng);
        });
      });'''
    contenu = contenu.replace(ancien_infra_click, nouveau_infra_click)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")