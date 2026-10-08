CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''  function loadParcelles() {
    return fetch('{% url "api_parcelles_toutes" %}')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        allParcelles = data;
        redessinerCouches();
        populateZoneFilter();
        populateOccupationFilter();
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {
          map.fitBounds(coucheParcelles.getBounds(), { padding: [20, 20] });
        }
        appliquerRechercheDepuisURL();
      })
      .catch(function (e) { console.error('Erreur parcelles:', e); });
  }'''

nouveau = '''  let coucheInfrastructures = null;

  function afficherIconesInfrastructures(data) {
    if (coucheInfrastructures) map.removeLayer(coucheInfrastructures);
    coucheInfrastructures = L.layerGroup();

    (data.features || []).forEach(function (feature) {
      const infras = feature.properties.infrastructures || [];
      infras.forEach(function (infra) {
        if (infra.latitude == null || infra.longitude == null) return;

        const icone = L.divIcon({
          className: '',
          html:
            '<div style="background:' + (infra.couleur || '#7b3fa0') + '; width:24px; height:24px; ' +
            'border-radius:50%; border:2px solid white; box-shadow:0 1px 4px rgba(0,0,0,0.4); ' +
            'display:flex; align-items:center; justify-content:center;">' +
              '<i class="fa-solid ' + (infra.icone || 'fa-map-pin') + '" style="color:white; font-size:11px;"></i>' +
            '</div>',
          iconSize: [24, 24],
          iconAnchor: [12, 12],
        });

        L.marker([infra.latitude, infra.longitude], { icon: icone })
          .bindPopup('<strong>' + infra.nom + '</strong><br><span style="color:#766c5d;">' + infra.categorie + '</span>')
          .addTo(coucheInfrastructures);
      });
    });

    coucheInfrastructures.addTo(map);
  }

  function loadParcelles() {
    return fetch('{% url "api_parcelles_toutes" %}')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        allParcelles = data;
        redessinerCouches();
        populateZoneFilter();
        populateOccupationFilter();
        afficherIconesInfrastructures(data);
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {
          map.fitBounds(coucheParcelles.getBounds(), { padding: [20, 20] });
        }
        appliquerRechercheDepuisURL();
      })
      .catch(function (e) { console.error('Erreur parcelles:', e); });
  }'''

if "afficherIconesInfrastructures" in contenu:
    print("DEJA FAIT : deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : icones d'infrastructures ajoutees sur la carte.")
else:
    print("ERREUR : bloc exact introuvable.")