# -*- coding: utf-8 -*-
"""
Ajoute, dans les fiches d'information du geoportail public :
  - Parcelle : affiche la distance depuis la position de l'utilisateur
    (le bouton Itineraire existait deja).
  - Infrastructure : affiche la distance depuis la position de
    l'utilisateur ET ajoute un bouton "Itineraire jusqu'ici" qui
    reutilise le calcul multi-modal existant (calculerItineraire).

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "infraRouteBtn"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Fiche parcelle : calcule la distance avant de construire le HTML ---
    ancien_centre = '''          const occInfo = fpOccupationInfo(props.occupation_sol);
          const centre = layer.getBounds().getCenter();

          const ficheHTML ='''
    if ancien_centre not in contenu:
        raise SystemExit("ANCRE 'const centre = layer.getBounds()' INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_centre = '''          const occInfo = fpOccupationInfo(props.occupation_sol);
          const centre = layer.getBounds().getCenter();

          let fpDistanceTexte = '';
          if (userLatLng) {
            const fpDist = L.latLng(userLatLng[0], userLatLng[1]).distanceTo(centre);
            fpDistanceTexte = fpDist >= 1000 ? (fpDist / 1000).toFixed(2) + ' km' : Math.round(fpDist) + ' m';
          }

          const ficheHTML ='''
    contenu = contenu.replace(ancien_centre, nouveau_centre)

    # --- 2) Fiche parcelle : ajoute la ligne "Distance" dans fp-rows ---
    ancienne_ligne = '''                (props.adresse_parcelle ? '<div class="fp-row"><span class="fp-label">Secteur</span><span class="fp-value">' + props.adresse_parcelle + '</span></div>' : '') +
              '</div>' +'''
    if ancienne_ligne not in contenu:
        raise SystemExit("ANCRE ligne 'Secteur' fiche parcelle INTROUVABLE - abandon partiel, verifie le fichier.")

    nouvelle_ligne = '''                (props.adresse_parcelle ? '<div class="fp-row"><span class="fp-label">Secteur</span><span class="fp-value">' + props.adresse_parcelle + '</span></div>' : '') +
                (fpDistanceTexte ? '<div class="fp-row"><span class="fp-label">Distance (votre position)</span><span class="fp-value">' + fpDistanceTexte + '</span></div>' : '') +
              '</div>' +'''
    contenu = contenu.replace(ancienne_ligne, nouvelle_ligne)

    # --- 3) Popup infrastructure : ajoute distance + bouton itineraire ---
    ancien_popup = '''  function construirePopupInfra(infra) {
    let html = '<div style="min-width:190px;">';
    html += '<strong>' + infra.nom + '</strong>';
    html += '<br><span style="color:#766c5d; font-size:12px;">' + (infra.sous_type || infra.categorie) + '</span>';
    const details = infra.details || {};
    const cles = Object.keys(details);
    if (cles.length > 0) {
      html += '<table style="font-size:12px; width:100%; margin-top:6px; border-top:1px solid #eee; padding-top:6px;">';
      cles.forEach(function (cle) {
        html += '<tr><td style="color:#766c5d; padding-right:10px; vertical-align:top;">' + cle + '</td><td style="font-weight:600;">' + details[cle] + '</td></tr>';
      });
      html += '</table>';
    }
    html += '</div>';
    return html;
  }'''
    if ancien_popup not in contenu:
        raise SystemExit("ANCRE construirePopupInfra INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_popup = '''  function construirePopupInfra(infra) {
    let html = '<div style="min-width:190px;">';
    html += '<strong>' + infra.nom + '</strong>';
    html += '<br><span style="color:#766c5d; font-size:12px;">' + (infra.sous_type || infra.categorie) + '</span>';
    const details = infra.details || {};
    const cles = Object.keys(details);
    if (cles.length > 0) {
      html += '<table style="font-size:12px; width:100%; margin-top:6px; border-top:1px solid #eee; padding-top:6px;">';
      cles.forEach(function (cle) {
        html += '<tr><td style="color:#766c5d; padding-right:10px; vertical-align:top;">' + cle + '</td><td style="font-weight:600;">' + details[cle] + '</td></tr>';
      });
      html += '</table>';
    }
    html += '<div id="infraDistance" style="margin-top:8px; font-size:12px; color:#766c5d;"></div>';
    html += '<button type="button" id="infraRouteBtn" style="margin-top:6px; width:100%; padding:6px; border:1px solid #d8cdb8; border-radius:6px; background:#fff; cursor:pointer; font-size:12px; color:#3c2a20;"><i class="fa-solid fa-route"></i> Itin\\u00e9raire jusqu\\'ici</button>';
    html += '</div>';
    return html;
  }'''
    contenu = contenu.replace(ancien_popup, nouveau_popup)

    # --- 4) Les marqueurs infra portent leurs coordonnees (pour le popupopen) ---
    ancien_marqueur = '''      L.marker([infra.latitude, infra.longitude], { icon: icone })
        .bindPopup(construirePopupInfra(infra))
        .addTo(coucheInfrastructures);
    });'''
    if ancien_marqueur not in contenu:
        raise SystemExit("ANCRE creation marqueur infra INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_marqueur = '''      const marqueurInfra = L.marker([infra.latitude, infra.longitude], { icon: icone })
        .bindPopup(construirePopupInfra(infra))
        .addTo(coucheInfrastructures);
      marqueurInfra.infraLat = infra.latitude;
      marqueurInfra.infraLng = infra.longitude;
    });'''
    contenu = contenu.replace(ancien_marqueur, nouveau_marqueur)

    # --- 5) Gestionnaire popupopen : remplit la distance + branche le bouton ---
    ancien_init = '''    basemaps.osm.addTo(map);
    ajouterControlesCarte();
    initialiserDessin();'''
    if ancien_init not in contenu:
        raise SystemExit("ANCRE init carte (basemaps/initialiserDessin) INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_init = '''    basemaps.osm.addTo(map);
    ajouterControlesCarte();
    initialiserDessin();

    map.on('popupopen', function (e) {
      const source = e.popup._source;
      if (source && typeof source.infraLat === 'number') {
        const champDistance = document.getElementById('infraDistance');
        if (champDistance) {
          if (userLatLng) {
            const d = L.latLng(userLatLng[0], userLatLng[1]).distanceTo(L.latLng(source.infraLat, source.infraLng));
            champDistance.innerHTML = '<i class="fa-solid fa-location-dot"></i> ' + (d >= 1000 ? (d / 1000).toFixed(1) + ' km' : Math.round(d) + ' m') + ' de votre position';
          } else {
            champDistance.innerHTML = '<span style="color:#b23b2e;">G\\u00e9olocalisez-vous pour voir la distance.</span>';
          }
        }
        const boutonRoute = document.getElementById('infraRouteBtn');
        if (boutonRoute) {
          boutonRoute.addEventListener('click', function () {
            calculerItineraire(source.infraLat, source.infraLng);
          });
        }
      }
    });'''
    contenu = contenu.replace(ancien_init, nouveau_init)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")