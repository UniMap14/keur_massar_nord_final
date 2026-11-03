# -*- coding: utf-8 -*-
"""
ADMIN - Feature 7 (derniere) : Zones sous-desservies / Voronoi ameliores
(respect du filtre categorie, limite stricte de la commune, comptage de
parcelles concernees, liste des quartiers critiques cliquables, Voronoi
clippe a la limite communale).

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "parcellesConcernees"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) analyserZonesSousDesservies : version enrichie ---
    ancien_desserte = '''  function analyserZonesSousDesservies() {
    const seuil = parseInt(document.getElementById('seuil-desserte').value, 10);
    const resultEl = document.getElementById('sousDesservisResult');
    if (coucheSousDesservis) { map.removeLayer(coucheSousDesservis); coucheSousDesservis = null; }

    const infras = toutesLesInfrastructures({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle })
      .filter(function (i) { return i.latitude != null && i.longitude != null; });
    if (infras.length === 0) { resultEl.innerHTML = '<span style="color:#b23b2e;">Aucune infrastructure à analyser.</span>'; return; }

    resultEl.textContent = 'Calcul en cours...';
    setTimeout(function () {
      const bounds = (coucheParcelles && coucheParcelles.getBounds().isValid()) ? coucheParcelles.getBounds() : map.getBounds();
      const pas = 0.0018;
      const groupe = L.layerGroup();
      let cellulesSousDesservies = 0, totalCellules = 0;

      for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += pas) {
        for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += pas) {
          totalCellules++;
          const point = L.latLng(lat, lng);
          let distMin = Infinity;
          for (let i = 0; i < infras.length; i++) {
            const d = point.distanceTo(L.latLng(infras[i].latitude, infras[i].longitude));
            if (d < distMin) distMin = d;
          }
          if (distMin > seuil) {
            cellulesSousDesservies++;
            L.rectangle([[lat - pas / 2, lng - pas / 2], [lat + pas / 2, lng + pas / 2]], { color: 'transparent', fillColor: '#b23b2e', fillOpacity: 0.35, weight: 0 }).addTo(groupe);
          }
        }
      }
      coucheSousDesservis = groupe;
      coucheSousDesservis.addTo(map);
      const pct = totalCellules > 0 ? Math.round((cellulesSousDesservies / totalCellules) * 100) : 0;
      const seuilTxt = seuil >= 1000 ? (seuil / 1000) + ' km' : seuil + ' m';
      resultEl.innerHTML = '<span style="color:#b23b2e;"><i class="fa-solid fa-triangle-exclamation"></i> ' + pct + '% du territoire affiché est à plus de ' + seuilTxt + ' de toute infrastructure</span>';
    }, 50);
  }'''
    if ancien_desserte not in contenu:
        raise SystemExit("ANCRE analyserZonesSousDesservies (admin) INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_desserte = '''  function analyserZonesSousDesservies() {
    const seuil = parseInt(document.getElementById('seuil-desserte').value, 10);
    const resultEl = document.getElementById('sousDesservisResult');

    if (coucheSousDesservis) { map.removeLayer(coucheSousDesservis); coucheSousDesservis = null; }

    const infras = infrastructuresFiltrees({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle });

    if (infras.length === 0) {
      resultEl.innerHTML = '<span style="color:#b23b2e;">Aucune infrastructure à analyser.</span>';
      return;
    }

    resultEl.textContent = 'Calcul en cours...';

    setTimeout(function () {
      const bounds = (allLimites && allLimites.features && allLimites.features.length)
        ? L.geoJSON(allLimites).getBounds()
        : ((coucheParcelles && coucheParcelles.getBounds().isValid()) ? coucheParcelles.getBounds() : map.getBounds());
      const pas = 0.0018; // environ 180 m a cette latitude
      const groupe = L.layerGroup();
      let cellulesSousDesservies = 0;
      let totalCellules = 0;
      const comptesParZone = {};

      for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += pas) {
        for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += pas) {
          if (!celluleDansLaCommune(lat, lng)) continue;
          totalCellules++;
          const point = L.latLng(lat, lng);
          let distMin = Infinity;
          for (let i = 0; i < infras.length; i++) {
            const d = point.distanceTo(L.latLng(infras[i].latitude, infras[i].longitude));
            if (d < distMin) distMin = d;
          }
          if (distMin > seuil) {
            cellulesSousDesservies++;
            L.rectangle(
              [[lat - pas / 2, lng - pas / 2], [lat + pas / 2, lng + pas / 2]],
              { color: 'transparent', fillColor: '#b23b2e', fillOpacity: 0.35, weight: 0 }
            ).addTo(groupe);

            if (typeof turf !== 'undefined' && allZones && allZones.features && allZones.features.length) {
              for (let z = 0; z < allZones.features.length; z++) {
                try {
                  if (turf.booleanPointInPolygon(turf.point([lng, lat]), allZones.features[z])) {
                    const nomZone = (allZones.features[z].properties || {}).nom || 'Zone inconnue';
                    comptesParZone[nomZone] = (comptesParZone[nomZone] || 0) + 1;
                    break;
                  }
                } catch (e) {}
              }
            }
          }
        }
      }

      coucheSousDesservis = groupe;
      coucheSousDesservis.addTo(map);

      const baseParcelles = (typeof filteredParcelles !== 'undefined' && filteredParcelles.length > 0) ? filteredParcelles : (allParcelles.features || []);
      let parcellesConcernees = 0;
      baseParcelles.forEach(function (f) {
        if (!f.geometry) return;
        let centre;
        try { centre = turf.centroid(f).geometry.coordinates; } catch (e) { return; }
        const point = L.latLng(centre[1], centre[0]);
        let distMin = Infinity;
        for (let i = 0; i < infras.length; i++) {
          const d = point.distanceTo(L.latLng(infras[i].latitude, infras[i].longitude));
          if (d < distMin) distMin = d;
        }
        if (distMin > seuil) parcellesConcernees++;
      });

      const pct = totalCellules > 0 ? Math.round((cellulesSousDesservies / totalCellules) * 100) : 0;
      const seuilTxt = seuil >= 1000 ? (seuil / 1000) + ' km' : seuil + ' m';

      const zonesTriees = Object.keys(comptesParZone).sort(function (a, b) { return comptesParZone[b] - comptesParZone[a]; }).slice(0, 5);
      let listeZonesHTML = '';
      if (zonesTriees.length) {
        listeZonesHTML = '<div class="geo-selection-liste" style="margin-top:8px;">' +
          zonesTriees.map(function (nom) {
            return '<div class="geo-selection-item" data-zone="' + echapperHtml(nom) + '"><span class="nom">' + echapperHtml(nom) + '</span><span class="val">' + comptesParZone[nom] + ' cellule(s)</span></div>';
          }).join('') + '</div>';
      }

      resultEl.innerHTML =
        '<span style="color:#b23b2e;"><i class="fa-solid fa-triangle-exclamation"></i> ' + pct + '% de la commune est à plus de ' + seuilTxt + ' de toute infrastructure' +
        (filtreInfraCategorie ? ' (' + filtreInfraCategorie + ')' : '') + '</span>' +
        '<div style="margin-top:4px; font-size:12px; color:#766c5d;">' + parcellesConcernees.toLocaleString('fr-FR') + ' parcelle(s) concernée(s)</div>' +
        listeZonesHTML;

      resultEl.querySelectorAll('.geo-selection-item').forEach(function (el) {
        el.style.cursor = 'pointer';
        el.addEventListener('click', function () {
          selectionnerQuartier(el.getAttribute('data-zone'));
        });
      });
    }, 50);
  }'''
    contenu = contenu.replace(ancien_desserte, nouveau_desserte)

    # --- 2) basculerVoronoi : version enrichie (clip a la commune) ---
    ancien_voronoi = '''  function basculerVoronoi(active) {
    if (coucheVoronoi) { map.removeLayer(coucheVoronoi); coucheVoronoi = null; }
    const resultEl = document.getElementById('voronoiResult');
    if (!active) { resultEl.textContent = ''; return; }
    if (typeof turf === 'undefined') { resultEl.innerHTML = '<span style="color:#b23b2e;">Bibliothèque Turf.js indisponible.</span>'; return; }

    const infras = toutesLesInfrastructures({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle })
      .filter(function (i) { return i.latitude != null && i.longitude != null; });
    if (infras.length < 3) { resultEl.innerHTML = '<span style="color:#b23b2e;">Il faut au moins 3 infrastructures.</span>'; return; }

    try {
      const points = turf.featureCollection(infras.map(function (i) { return turf.point([i.longitude, i.latitude], { nom: i.nom, categorie: i.categorie }); }));
      const bounds = (coucheParcelles && coucheParcelles.getBounds().isValid()) ? coucheParcelles.getBounds() : map.getBounds();
      const bbox = [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()];
      const voronoiPolygones = turf.voronoi(points, { bbox: bbox });

      coucheVoronoi = L.geoJSON(voronoiPolygones, {
        style: function () { return { color: '#6b4a35', weight: 1.3, fillColor: '#c9982e', fillOpacity: 0.06, dashArray: '3 4' }; },
        onEachFeature: function (feature, layer) {
          const idx = voronoiPolygones.features.indexOf(feature);
          const infra = infras[idx];
          if (infra) layer.bindPopup('<strong>Zone de desserte</strong><br>' + infra.nom + '<br><span style="color:#766c5d; font-size:12px;">' + infra.categorie + '</span>');
        }
      }).addTo(map);
      resultEl.innerHTML = '<span style="color:#2f7a4f;"><i class="fa-solid fa-circle-check"></i> ' + infras.length + ' zones de desserte calculées</span>';
    } catch (e) {
      console.error('Erreur Voronoi:', e);
      resultEl.innerHTML = '<span style="color:#b23b2e;">Erreur lors du calcul des zones de desserte.</span>';
    }
  }'''
    if ancien_voronoi not in contenu:
        raise SystemExit("ANCRE basculerVoronoi (admin) INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_voronoi = '''  function basculerVoronoi(active) {
    if (coucheVoronoi) { map.removeLayer(coucheVoronoi); coucheVoronoi = null; }
    const resultEl = document.getElementById('voronoiResult');
    if (!active) { resultEl.textContent = ''; return; }

    if (typeof turf === 'undefined') {
      resultEl.innerHTML = '<span style="color:#b23b2e;">Bibliothèque Turf.js indisponible.</span>';
      return;
    }

    const infras = infrastructuresFiltrees({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle });

    if (infras.length < 3) {
      resultEl.innerHTML = '<span style="color:#b23b2e;">Il faut au moins 3 infrastructures pour calculer des zones de desserte.</span>';
      return;
    }

    try {
      const points = turf.featureCollection(
        infras.map(function (i) { return turf.point([i.longitude, i.latitude], { nom: i.nom, categorie: i.categorie, couleur: i.couleur }); })
      );
      const bounds = (allLimites && allLimites.features && allLimites.features.length)
        ? L.geoJSON(allLimites).getBounds()
        : ((coucheParcelles && coucheParcelles.getBounds().isValid()) ? coucheParcelles.getBounds() : map.getBounds());
      const bbox = [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()];

      const voronoiPolygones = turf.voronoi(points, { bbox: bbox });

      voronoiPolygones.features.forEach(function (f, idx) {
        if (!f) return;
        f.properties = f.properties || {};
        const infra = infras[idx];
        if (infra) { f.properties.nom = infra.nom; f.properties.categorie = infra.categorie; }
      });

      let limiteUnion = null;
      if (allLimites && allLimites.features && allLimites.features.length) {
        limiteUnion = allLimites.features[0];
        for (let i = 1; i < allLimites.features.length; i++) {
          try { limiteUnion = turf.union(limiteUnion, allLimites.features[i]); } catch (e) {}
        }
      }

      if (limiteUnion) {
        voronoiPolygones.features = voronoiPolygones.features
          .filter(function (f) { return f && f.geometry; })
          .map(function (f) {
            try {
              const clip = turf.intersect(f, limiteUnion);
              if (clip) { clip.properties = f.properties; return clip; }
              return null;
            } catch (e) { return f; }
          })
          .filter(function (f) { return f && f.geometry; });
      }

      coucheVoronoi = L.geoJSON(voronoiPolygones, {
        style: function () {
          return { color: '#6b4a35', weight: 1.3, fillColor: '#c9982e', fillOpacity: 0.06, dashArray: '3 4' };
        },
        onEachFeature: function (feature, layer) {
          const props = feature.properties || {};
          if (props.nom) {
            layer.bindPopup('<strong>Zone de desserte</strong><br>' + props.nom + '<br><span style="color:#766c5d; font-size:12px;">' + (props.categorie || '') + '</span>');
          }
        }
      }).addTo(map);

      resultEl.innerHTML = '<span style="color:#2f7a4f;"><i class="fa-solid fa-circle-check"></i> ' + infras.length + ' zones de desserte calculées' +
        (filtreInfraCategorie ? ' (' + filtreInfraCategorie + ')' : '') + '</span>';
    } catch (e) {
      console.error('Erreur Voronoi:', e);
      resultEl.innerHTML = '<span style="color:#b23b2e;">Erreur lors du calcul des zones de desserte.</span>';
    }
  }'''
    contenu = contenu.replace(ancien_voronoi, nouveau_voronoi)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes (feature 7 : desserte + Voronoi ameliores).")