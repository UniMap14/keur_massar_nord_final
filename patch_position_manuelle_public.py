# -*- coding: utf-8 -*-
import io

CHEMIN = "foncier/templates/foncier/geoportail.html"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    lignes = f.readlines()


def trouver(sous_chaine, depart=0):
    for i in range(depart, len(lignes)):
        if sous_chaine in lignes[i]:
            return i
    raise ValueError("Introuvable : " + sous_chaine)


idx_onevent = trouver("onEvent('btnGeolocaliser'")
lignes[idx_onevent + 1:idx_onevent + 1] = [
    "    onEvent('btnPositionManuelle', 'click', activerPositionManuelle);\n"
]
print("OK 1/4 : clic sur 'Definir ma position' cable")


idx_debut_fn = trouver("function localiserMoi() {")
idx_calc = trouver("function calculerItineraire", idx_debut_fn)
idx_fin_fn = idx_calc - 2

nouveau_bloc = """  let modePositionManuelle = false;

  const BORNES_SENEGAL = { latMin: 12.0, latMax: 16.7, lngMin: -17.6, lngMax: -11.3 };

  function positionDansSenegal(lat, lng) {
    return lat >= BORNES_SENEGAL.latMin && lat <= BORNES_SENEGAL.latMax &&
      lng >= BORNES_SENEGAL.lngMin && lng <= BORNES_SENEGAL.lngMax;
  }

  function creerIconePosition() {
    return L.divIcon({
      className: '',
      html: '<div style="background:#c9982e; width:16px; height:16px; border-radius:50%; border:3px solid white; box-shadow:0 0 6px rgba(0,0,0,0.5);"></div>',
      iconSize: [16, 16]
    });
  }

  function localiserMoi() {
    const status = document.getElementById('position-status');

    if (!navigator.geolocation) {
      status.innerHTML = '<span style="color:red;">Géolocalisation non supportée par ce navigateur.</span>';
      return;
    }

    status.textContent = 'Localisation en cours...';

    navigator.geolocation.getCurrentPosition(
      function (pos) {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;

        if (!positionDansSenegal(lat, lng)) {
          status.innerHTML = '<span style="color:#dc3545;"><i class="fa-solid fa-triangle-exclamation"></i> Position détectée hors du Sénégal (' + lat.toFixed(2) + ', ' + lng.toFixed(2) + '). Cela vient souvent d\\'une géolocalisation par IP imprécise sur ordinateur. Utilise le bouton « Définir ma position sur la carte » ci-dessous.</span>';
          return;
        }

        userLatLng = [lat, lng];
        if (userMarker) map.removeLayer(userMarker);
        userMarker = L.marker(userLatLng, { icon: creerIconePosition() }).addTo(map).bindPopup('Vous êtes ici');
        map.flyTo(userLatLng, 15);
        status.innerHTML = '<span style="color:green;"><i class="fa-solid fa-check"></i> Position trouvée.</span>';
        afficherInfrastructuresProches();
      },
      function (err) {
        status.innerHTML = '<span style="color:red;">Impossible de récupérer votre position (' + err.message + ').</span>';
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  function activerPositionManuelle() {
    modePositionManuelle = true;
    const status = document.getElementById('position-status');
    status.innerHTML = '<span style="color:#766c5d;"><i class="fa-solid fa-hand-pointer"></i> Clique sur la carte, à l\\'endroit où tu te trouves...</span>';
    map.getContainer().style.cursor = 'crosshair';
  }

  function definirPositionManuelle(latlng) {
    modePositionManuelle = false;
    map.getContainer().style.cursor = '';

    userLatLng = [latlng.lat, latlng.lng];
    if (userMarker) map.removeLayer(userMarker);
    userMarker = L.marker(userLatLng, { icon: creerIconePosition() }).addTo(map).bindPopup('Votre position (définie manuellement)');

    const status = document.getElementById('position-status');
    status.innerHTML = '<span style="color:green;"><i class="fa-solid fa-check"></i> Position définie manuellement.</span>';
    afficherInfrastructuresProches();
  }

"""

lignes[idx_debut_fn:idx_fin_fn + 1] = [nouveau_bloc]
print("OK 2/4 : localiserMoi() mise a jour + nouvelles fonctions ajoutees")


idx_mapinit = trouver("map = L.map(")
lignes[idx_mapinit + 1:idx_mapinit + 1] = [
    "    map.on('click', function (e) {\n",
    "      if (modePositionManuelle) definirPositionManuelle(e.latlng);\n",
    "    });\n",
]
print("OK 3/4 : ecoute du clic sur la carte ajoutee")


idx_geolocbtn = trouver('id="btnGeolocaliser"')
idx_fin_geolocbtn = trouver("</button>", idx_geolocbtn)
lignes[idx_fin_geolocbtn + 1:idx_fin_geolocbtn + 1] = [
    '        <button id="btnPositionManuelle" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:6px;">\n',
    '          <i class="fa-solid fa-map-pin"></i> Definir ma position sur la carte\n',
    '        </button>\n',
]
print("OK 4/4 : bouton ajoute")


with io.open(CHEMIN, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lignes)

print("")
print("Fichier sauvegarde : " + CHEMIN)
