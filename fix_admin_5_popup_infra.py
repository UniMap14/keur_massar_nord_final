# -*- coding: utf-8 -*-
"""
ADMIN - Feature 5/6 : distance + bouton itineraire dans le popup
infrastructure (construirePopupInfra + infraLat/infraLng sur le marqueur
+ handler popupopen).

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "infraRouteBtn"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) construirePopupInfra : ajouter distance + bouton itineraire ---
    ancien_popup = '''    if (peutTechnique && infra.id) {
      html += '<a href="' + URL_INFRA_UPDATE_TEMPLATE.replace('0', infra.id) + '" target="_blank" rel="noopener" style="display:inline-block; margin-top:8px; font-size:12px; font-weight:700; color:#2f7a4f; text-decoration:none;"><i class="fa-solid fa-pen"></i> Modifier cette infrastructure</a>';
    }
    html += '</div>';
    return html;
  }'''
    if ancien_popup not in contenu:
        raise SystemExit("ANCRE construirePopupInfra INTROUVABLE - abandon, rien n'a ete modifie.")
    nouveau_popup = '''    if (peutTechnique && infra.id) {
      html += '<a href="' + URL_INFRA_UPDATE_TEMPLATE.replace('0', infra.id) + '" target="_blank" rel="noopener" style="display:inline-block; margin-top:8px; font-size:12px; font-weight:700; color:#2f7a4f; text-decoration:none;"><i class="fa-solid fa-pen"></i> Modifier cette infrastructure</a>';
    }
    html += '<div id="infraDistance" style="margin-top:8px; font-size:12px; color:#766c5d;"></div>';
    html += '<button type="button" id="infraRouteBtn" style="margin-top:6px; width:100%; padding:6px; border:1px solid #d8cdb8; border-radius:6px; background:#fff; cursor:pointer; font-size:12px; color:#3c2a20;"><i class="fa-solid fa-route"></i> Itinéraire jusqu\\'ici</button>';
    html += '</div>';
    return html;
  }'''
    contenu = contenu.replace(ancien_popup, nouveau_popup)

    # --- 2) Creation du marqueur infra : stocker infraLat/infraLng ---
    ancien_marker = "      L.marker([infra.latitude, infra.longitude], { icon: icone }).bindPopup(construirePopupInfra(infra)).addTo(coucheInfrastructures);"
    if ancien_marker not in contenu:
        raise SystemExit("ANCRE creation marqueur infra INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_marker = '''      const marqueurInfra = L.marker([infra.latitude, infra.longitude], { icon: icone })
        .bindPopup(construirePopupInfra(infra))
        .addTo(coucheInfrastructures);
      marqueurInfra.infraLat = infra.latitude;
      marqueurInfra.infraLng = infra.longitude;'''
    contenu = contenu.replace(ancien_marker, nouveau_marker)

    # --- 3) Handler popupopen, juste apres initialiserDessin(); ---
    ancien_init = '''    basemaps.osm.addTo(map);
    ajouterControlesCarte();
    initialiserDessin();

    map.on('click', function (e) {
      if (modeChoixRayon) {'''
    if ancien_init not in contenu:
        raise SystemExit("ANCRE initialiserDessin()/map.on('click') INTROUVABLE - abandon partiel, verifie le fichier.")
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
            champDistance.innerHTML = '<span style="color:#b23b2e;">Géolocalisez-vous pour voir la distance.</span>';
          }
        }
        const boutonRoute = document.getElementById('infraRouteBtn');
        if (boutonRoute) {
          boutonRoute.addEventListener('click', function () {
            calculerItineraire(source.infraLat, source.infraLng);
          });
        }
      }
    });

    map.on('click', function (e) {
      if (modeChoixRayon) {'''
    contenu = contenu.replace(ancien_init, nouveau_init)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes (feature 5/6 : distance + itineraire dans le popup infra).")