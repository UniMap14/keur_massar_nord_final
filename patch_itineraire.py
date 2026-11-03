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


idx_debut = trouver('<div id="route-info"')
idx_btn = trouver("btnEffacerItineraire", idx_debut)
idx_fin = trouver("</div>", idx_btn)

nouveau_panneau = [
    '        <div id="route-info" style="margin-top:8px; font-size:13px; display:none;">\n',
    '          <div style="font-size:11px; color:#766c5d; margin-bottom:6px;">Depuis votre position jusqu\'a la parcelle</div>\n',
    '          <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #e6ded0;">\n',
    '            <span><i class="fa-solid fa-person-walking" style="width:18px; color:#766c5d;"></i> A pied</span>\n',
    '            <span id="route-pied" style="font-weight:700; color:#3c2a20;"></span>\n',
    '          </div>\n',
    '          <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #e6ded0;">\n',
    '            <span><i class="fa-solid fa-bicycle" style="width:18px; color:#766c5d;"></i> Velo</span>\n',
    '            <span id="route-velo" style="font-weight:700; color:#3c2a20;"></span>\n',
    '          </div>\n',
    '          <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #e6ded0;">\n',
    '            <span><i class="fa-solid fa-motorcycle" style="width:18px; color:#766c5d;"></i> Moto <span style="font-size:10px; color:#766c5d;">(estime)</span></span>\n',
    '            <span id="route-moto" style="font-weight:700; color:#3c2a20;"></span>\n',
    '          </div>\n',
    '          <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0;">\n',
    '            <span><i class="fa-solid fa-car" style="width:18px; color:#766c5d;"></i> Voiture</span>\n',
    '            <span id="route-voiture" style="font-weight:700; color:#3c2a20;"></span>\n',
    '          </div>\n',
    '          <button id="btnEffacerItineraire" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:10px;">\n',
    '            <i class="fa-solid fa-xmark"></i> Effacer l\'itineraire\n',
    '          </button>\n',
    '        </div>\n',
]

lignes[idx_debut:idx_fin + 1] = nouveau_panneau
print("OK 1/5 : panneau route-info remplace (" + str(idx_fin - idx_debut + 1) + " lignes -> " + str(len(nouveau_panneau)) + " lignes)")


idx_debut_fn = trouver("function calculerItineraire(lat, lng) {")
idx_effacer = trouver("function effacerItineraire()", idx_debut_fn)
idx_fin_fn = idx_effacer - 2

nouvelle_fonction = """  function calculerItineraire(lat, lng) {
    const status = document.getElementById('position-status');

    if (!userLatLng) {
      status.innerHTML = '<span style="color:#dc3545;"><i class="fa-solid fa-triangle-exclamation"></i> Clique d\\'abord sur « Me géolocaliser » pour définir ton point de départ.</span>';
      return;
    }

    fermerPopup();
    status.innerHTML = '<span style="color:#766c5d;"><i class="fa-solid fa-spinner fa-spin"></i> Calcul de l\\'itinéraire...</span>';

    const origine = userLatLng[1] + ',' + userLatLng[0];
    const destination = lng + ',' + lat;

    const urlVoiture = 'https://router.project-osrm.org/route/v1/driving/' + origine + ';' + destination + '?overview=full&geometries=geojson';
    const urlVelo = 'https://routing.openstreetmap.de/routed-bike/route/v1/bike/' + origine + ';' + destination + '?overview=full&geometries=geojson';
    const urlPied = 'https://routing.openstreetmap.de/routed-foot/route/v1/foot/' + origine + ';' + destination + '?overview=full&geometries=geojson';

    function recupererRoute(url) {
      return fetch(url).then(function (r) { return r.json(); }).catch(function () { return null; });
    }

    function formaterMode(distanceM, dureeS) {
      return (distanceM / 1000).toFixed(2) + ' km - ' + Math.round(dureeS / 60) + ' min';
    }

    Promise.all([recupererRoute(urlVoiture), recupererRoute(urlVelo), recupererRoute(urlPied)])
      .then(function (resultats) {
        const dataVoiture = resultats[0];
        const dataVelo = resultats[1];
        const dataPied = resultats[2];

        if (!dataVoiture || !dataVoiture.routes || !dataVoiture.routes.length) {
          status.innerHTML = '<span style="color:#dc3545;"><i class="fa-solid fa-triangle-exclamation"></i> Aucun itinéraire trouvé jusqu\\'à cette parcelle.</span>';
          return;
        }

        const routeVoiture = dataVoiture.routes[0];
        if (coucheItineraire) map.removeLayer(coucheItineraire);
        coucheItineraire = L.geoJSON(routeVoiture.geometry, {
          style: { color: '#ff6600', weight: 5 }
        }).addTo(map);
        map.fitBounds(coucheItineraire.getBounds(), { padding: [50, 50] });

        document.getElementById('route-voiture').textContent = formaterMode(routeVoiture.distance, routeVoiture.duration);

        const vitesseMotoKmh = 38;
        const dureeMotoS = (routeVoiture.distance / 1000 / vitesseMotoKmh) * 3600;
        document.getElementById('route-moto').textContent = formaterMode(routeVoiture.distance, dureeMotoS);

        if (dataVelo && dataVelo.routes && dataVelo.routes.length) {
          const routeVelo = dataVelo.routes[0];
          document.getElementById('route-velo').textContent = formaterMode(routeVelo.distance, routeVelo.duration);
        } else {
          document.getElementById('route-velo').textContent = 'indisponible';
        }

        if (dataPied && dataPied.routes && dataPied.routes.length) {
          const routePied = dataPied.routes[0];
          document.getElementById('route-pied').textContent = formaterMode(routePied.distance, routePied.duration);
        } else {
          document.getElementById('route-pied').textContent = 'indisponible';
        }

        document.getElementById('route-info').style.display = 'block';
        status.innerHTML = '<span style="color:green;"><i class="fa-solid fa-check"></i> Itinéraire calculé.</span>';
      })
      .catch(function (e) {
        console.error('Erreur itineraire:', e);
        status.innerHTML = '<span style="color:#dc3545;"><i class="fa-solid fa-triangle-exclamation"></i> Erreur lors du calcul de l\\'itinéraire. Réessaie plus tard.</span>';
      });
  }

"""

lignes[idx_debut_fn:idx_fin_fn + 1] = [nouvelle_fonction]
print("OK 2/5 : calculerItineraire() reecrite (4 modes)")


idx_shareget = trouver("const shareBtn = document.getElementById('fpShareBtn')")
idx_fin_settimeout = None
for i in range(idx_shareget, len(lignes)):
    if "}, 0);" in lignes[i]:
        idx_fin_settimeout = i
        break
if idx_fin_settimeout is None:
    raise ValueError("Fin du setTimeout introuvable apres fpShareBtn")

cablage_route_btn = [
    "            const routeBtn = document.getElementById('fpRouteBtn');\n",
    "            if (routeBtn) routeBtn.addEventListener('click', function () {\n",
    "              calculerItineraire(centre.lat, centre.lng);\n",
    "            });\n",
]
lignes[idx_fin_settimeout:idx_fin_settimeout] = cablage_route_btn
print("OK 3/5 : clic sur le bouton Itineraire cable (appelle calculerItineraire)")


idx_sharebtn_html = trouver('id="fpShareBtn" title="Partager"')
ligne_source = lignes[idx_sharebtn_html]
indent = ligne_source[:len(ligne_source) - len(ligne_source.lstrip())]
nouvelle_ligne_bouton = (
    indent
    + "'<button type=\"button\" class=\"fp-btn-ghost\" id=\"fpRouteBtn\" title=\"Itineraire\"><i class=\"fa-solid fa-route\"></i></button>' +\n"
)
lignes[idx_sharebtn_html + 1:idx_sharebtn_html + 1] = [nouvelle_ligne_bouton]
print("OK 4/5 : bouton Itineraire ajoute dans la fiche parcelle (fp-footer)")


idx_occinfo = trouver("const occInfo = fpOccupationInfo(props.occupation_sol);")
ligne_occ = lignes[idx_occinfo]
indent_occ = ligne_occ[:len(ligne_occ) - len(ligne_occ.lstrip())]
ligne_centre = indent_occ + "const centre = layer.getBounds().getCenter();\n"
lignes[idx_occinfo + 1:idx_occinfo + 1] = [ligne_centre]
print("OK 5/5 : capture du centre de la parcelle ajoutee (centre.lat / centre.lng)")


with io.open(CHEMIN, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lignes)

print("")
print("Fichier sauvegarde : " + CHEMIN)
