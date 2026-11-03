# -*- coding: utf-8 -*-
"""
Ajoute, au clic sur "Me geolocaliser" :
  - la zone/quartier dans laquelle se trouve le visiteur (via Turf.js
    et les zones deja chargees sur la carte) ;
  - si le visiteur est un citoyen connecte relie a une parcelle : sa
    parcelle affichee en surbrillance sur la carte + la distance
    jusqu'a elle.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "function afficherZoneEtParcelle"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Variable JS pour la parcelle du citoyen connecte ---
    ancien_var = "  let allZones = { type: 'FeatureCollection', features: [] };"
    if ancien_var not in contenu:
        raise SystemExit("ANCRE 'allZones' INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_var = (
        ancien_var + "\n"
        "  let mesParcellesLayer = null;\n"
        "  const mesParcellesGeojson = {{ mes_parcelles_geojson|default:\"null\"|safe }};"
    )
    contenu = contenu.replace(ancien_var, nouveau_var)

    # --- 2) Appel de la nouvelle fonction juste apres la localisation reussie ---
    ancien_appel = "        afficherInfrastructuresProches();"
    if ancien_appel not in contenu:
        raise SystemExit("ANCRE appel afficherInfrastructuresProches INTROUVABLE - abandon partiel, verifie le fichier.")

    nouvel_appel = (
        ancien_appel + "\n"
        "        afficherZoneEtParcelle(pos.coords.latitude, pos.coords.longitude);"
    )
    contenu = contenu.replace(ancien_appel, nouvel_appel)

    # --- 3) Definition de la fonction, juste avant calculerItineraire ---
    ancre_fonction = "  function calculerItineraire(lat, lng) {"
    if ancre_fonction not in contenu:
        raise SystemExit("ANCRE calculerItineraire INTROUVABLE - abandon partiel, verifie le fichier.")

    nouvelle_fonction = '''  function afficherZoneEtParcelle(lat, lng) {
    const status = document.getElementById('position-status');
    let messageSupplementaire = '';

    if (typeof turf !== 'undefined' && allZones && allZones.features && allZones.features.length) {
      const point = turf.point([lng, lat]);
      let zoneTrouvee = null;
      for (let i = 0; i < allZones.features.length; i++) {
        try {
          if (turf.booleanPointInPolygon(point, allZones.features[i])) {
            zoneTrouvee = allZones.features[i];
            break;
          }
        } catch (e) {}
      }
      if (zoneTrouvee) {
        const proprietes = zoneTrouvee.properties || {};
        const nomZone = proprietes.nom || proprietes.layer || 'zone inconnue';
        messageSupplementaire += '<div style="margin-top:4px;"><i class="fa-solid fa-draw-polygon"></i> Vous \\u00eates dans : <strong>' + nomZone + '</strong></div>';
      } else {
        messageSupplementaire += '<div style="margin-top:4px; color:#766c5d;"><i class="fa-solid fa-draw-polygon"></i> Hors des zones cartographi\\u00e9es.</div>';
      }
    }

    if (mesParcellesGeojson && mesParcellesGeojson.features && mesParcellesGeojson.features.length) {
      if (mesParcellesLayer) map.removeLayer(mesParcellesLayer);
      mesParcellesLayer = L.geoJSON(mesParcellesGeojson, {
        style: { color: '#2f7a4f', weight: 3, fillColor: '#2f7a4f', fillOpacity: 0.25 }
      }).addTo(map);

      if (typeof turf !== 'undefined') {
        const pointUtilisateur = turf.point([lng, lat]);
        let plusProche = null;
        let distanceMin = Infinity;
        mesParcellesGeojson.features.forEach(function (feature) {
          try {
            const centre = turf.centroid(feature);
            const d = turf.distance(pointUtilisateur, centre, { units: 'kilometers' });
            if (d < distanceMin) { distanceMin = d; plusProche = feature; }
          } catch (e) {}
        });
        if (plusProche) {
          const proprietes = plusProche.properties || {};
          const nicad = proprietes.nicad || '';
          const distanceTexte = distanceMin < 1
            ? Math.round(distanceMin * 1000) + ' m'
            : distanceMin.toFixed(2) + ' km';
          messageSupplementaire += '<div style="margin-top:4px;"><i class="fa-solid fa-house"></i> Votre parcelle ' + nicad + ' est \\u00e0 ' + distanceTexte + '.</div>';
        }
      }
    }

    if (messageSupplementaire) {
      status.innerHTML += messageSupplementaire;
    }
  }

'''
    contenu = contenu.replace(ancre_fonction, nouvelle_fonction + ancre_fonction)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")