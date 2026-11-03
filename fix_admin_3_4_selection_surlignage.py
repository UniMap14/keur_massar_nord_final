# -*- coding: utf-8 -*-
"""
ADMIN - Features 3/6 + 4/6 combinees :
  3) Selection spatiale enrichie (zones touchees, infrastructures dans la
     zone, bouton "Itineraire vers cette zone").
  4) Surlignage rouge au clic sur une infrastructure de cette liste.
(Les deux sont lies : la liste du resultat 3 appelle la fonction de
surlignage 4, donc on les applique ensemble pour eviter une reference
cassee entre les deux patches.)

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "formeSelectionActuelle"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Nouvelles variables globales ---
    ancien_globals = '''  let selectionFeatures = [];
  let selectionSet = new Set();
  const cacheBbox = new WeakMap();'''
    if ancien_globals not in contenu:
        raise SystemExit("ANCRE globals (selectionFeatures/selectionSet) INTROUVABLE - abandon, rien n'a ete modifie.")
    nouveau_globals = '''  let selectionFeatures = [];
  let selectionSet = new Set();
  let formeSelectionActuelle = null;
  let selectionZones = [];
  let selectionInfra = [];
  let coucheInfraSurlignee = null;
  const cacheBbox = new WeakMap();'''
    contenu = contenu.replace(ancien_globals, nouveau_globals)

    # --- 2) surFormeDessinee : memoriser la forme ---
    ancien_sfd = '''    }).addTo(map);
    calculerSelection(forme);
  }'''
    if ancien_sfd not in contenu:
        raise SystemExit("ANCRE surFormeDessinee INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_sfd = '''    }).addTo(map);
    formeSelectionActuelle = forme;
    calculerSelection(forme);
  }'''
    contenu = contenu.replace(ancien_sfd, nouveau_sfd)

    # --- 3) calculerSelection : ajouter zonesTouchees + infraTouchees ---
    ancien_calc = '''        try { if (turf.booleanIntersects(f, forme)) trouvees.push(f); } catch (err) {}
      });
      selectionFeatures = trouvees;
      selectionSet = new Set(trouvees);
      afficherResultatSelection();
      redessinerCouches();
    }, 30);
  }'''
    if ancien_calc not in contenu:
        raise SystemExit("ANCRE calculerSelection INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_calc = '''        try { if (turf.booleanIntersects(f, forme)) trouvees.push(f); } catch (err) {}
      });

      const zonesTouchees = [];
      (allZones.features || []).forEach(function (z) {
        try {
          if (turf.booleanIntersects(z, forme)) {
            const p = z.properties || {};
            zonesTouchees.push(p.nom || p.layer || 'zone inconnue');
          }
        } catch (err) {}
      });

      const infraTouchees = [];
      toutesLesInfrastructures({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle }).forEach(function (infra) {
        if (infra.latitude == null || infra.longitude == null) return;
        try {
          if (turf.booleanPointInPolygon(turf.point([infra.longitude, infra.latitude]), forme)) {
            infraTouchees.push(infra);
          }
        } catch (err) {}
      });

      selectionZones = zonesTouchees;
      selectionInfra = infraTouchees;
      selectionFeatures = trouvees;
      selectionSet = new Set(trouvees);
      afficherResultatSelection();
      redessinerCouches();
    }, 30);
  }'''
    contenu = contenu.replace(ancien_calc, nouveau_calc)

    # --- 4) afficherResultatSelection : ajouter #selZones et #selInfraSection ---
    ancien_affich = '''    document.getElementById('selOccupation').textContent = Object.keys(compteOcc)
      .sort(function (a, b) { return compteOcc[b] - compteOcc[a]; }).slice(0, 3)
      .map(function (o) { return o + ' : ' + compteOcc[o]; }).join(' · ');

    if (selectionFeatures.length === 0) {'''
    if ancien_affich not in contenu:
        raise SystemExit("ANCRE afficherResultatSelection INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_affich = '''    document.getElementById('selOccupation').textContent = Object.keys(compteOcc)
      .sort(function (a, b) { return compteOcc[b] - compteOcc[a]; }).slice(0, 3)
      .map(function (o) { return o + ' : ' + compteOcc[o]; }).join(' · ');

    const zonesUniques = Array.from(new Set(selectionZones));
    const champZones = document.getElementById('selZones');
    if (champZones) {
      champZones.textContent = zonesUniques.length
        ? 'Quartiers couverts : ' + zonesUniques.join(', ')
        : '';
    }

    const sectionInfra = document.getElementById('selInfraSection');
    const listeInfra = document.getElementById('selInfraListe');
    if (sectionInfra && listeInfra) {
      if (selectionInfra.length) {
        listeInfra.innerHTML = selectionInfra.map(function (i) {
          return '<div class="geo-selection-item" data-lat="' + i.latitude + '" data-lng="' + i.longitude + '"><span class="nom">' + echapperHtml(i.nom || 'Infrastructure') + '</span></div>';
        }).join('');
        sectionInfra.style.display = 'block';
        listeInfra.querySelectorAll('.geo-selection-item').forEach(function (el) {
          el.style.cursor = 'pointer';
          el.addEventListener('click', function () {
            const lat = parseFloat(el.getAttribute('data-lat'));
            const lng = parseFloat(el.getAttribute('data-lng'));
            surlignerInfrastructure(lat, lng);
          });
        });
      } else {
        listeInfra.innerHTML = '';
        sectionInfra.style.display = 'none';
      }
    }

    if (selectionFeatures.length === 0) {'''
    contenu = contenu.replace(ancien_affich, nouveau_affich)

    # --- 5) Nouvelle fonction surlignerInfrastructure, juste avant effacerSelection ---
    ancien_avant_effacer = '''  function effacerSelection() {
    arreterDessin();
    if (coucheFormeSelection) { map.removeLayer(coucheFormeSelection); coucheFormeSelection = null; }
    selectionFeatures = [];
    selectionSet = new Set();
    const bloc = document.getElementById('selection-resultat');
    if (bloc) bloc.style.display = 'none';
    definirAideSelection('Choisissez une forme, puis dessinez-la sur la carte.');
    redessinerCouches();
  }'''
    if ancien_avant_effacer not in contenu:
        raise SystemExit("ANCRE effacerSelection (admin) INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_avant_effacer = '''  function surlignerInfrastructure(lat, lng) {
    if (isNaN(lat) || isNaN(lng)) return;
    if (coucheInfraSurlignee) { map.removeLayer(coucheInfraSurlignee); coucheInfraSurlignee = null; }
    coucheInfraSurlignee = L.circleMarker([lat, lng], {
      radius: 10,
      color: '#ffffff',
      weight: 2,
      fillColor: '#d12f2f',
      fillOpacity: 0.95
    }).addTo(map);
    map.flyTo([lat, lng], Math.max(map.getZoom(), 18));
  }

  function effacerSelection() {
    arreterDessin();
    if (coucheFormeSelection) { map.removeLayer(coucheFormeSelection); coucheFormeSelection = null; }
    selectionFeatures = [];
    selectionSet = new Set();
    formeSelectionActuelle = null;
    selectionZones = [];
    selectionInfra = [];
    if (coucheInfraSurlignee) { map.removeLayer(coucheInfraSurlignee); coucheInfraSurlignee = null; }
    const bloc = document.getElementById('selection-resultat');
    if (bloc) bloc.style.display = 'none';
    definirAideSelection('Choisissez une forme, puis dessinez-la sur la carte.');
    redessinerCouches();
  }'''
    contenu = contenu.replace(ancien_avant_effacer, nouveau_avant_effacer)

    # --- 6) HTML : #selZones, #selInfraSection, bouton btnSelectionItineraire ---
    ancien_html = '''          <div id="selOccupation" class="geo-tool-result" style="color:#766c5d;"></div>
          <div id="selection-liste" class="geo-selection-liste"></div>
          <div style="display:flex; gap:8px; margin-top:10px;">
            <button type="button" id="btnSelectionCSV" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-file-csv"></i> CSV</button>
            <button type="button" id="btnSelectionGeoJSON" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-map"></i> GeoJSON</button>
          </div>
          <button type="button" id="btnSelectionEffacer" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:8px;"><i class="fa-solid fa-trash"></i> Effacer la sélection</button>'''
    if ancien_html not in contenu:
        raise SystemExit("ANCRE HTML panneau selection-resultat INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_html = '''          <div id="selOccupation" class="geo-tool-result" style="color:#766c5d;"></div>
          <div id="selZones" class="geo-tool-result" style="color:#766c5d;"></div>
          <div id="selection-liste" class="geo-selection-liste"></div>
          <div id="selInfraSection" style="margin-top:8px; display:none;">
            <label class="geo-field-label" style="margin-top:0;">Infrastructures dans la zone</label>
            <div id="selInfraListe" class="geo-selection-liste"></div>
          </div>
          <div style="display:flex; gap:8px; margin-top:10px;">
            <button type="button" id="btnSelectionCSV" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-file-csv"></i> CSV</button>
            <button type="button" id="btnSelectionGeoJSON" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-map"></i> GeoJSON</button>
          </div>
          <button type="button" id="btnSelectionItineraire" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:8px;"><i class="fa-solid fa-route"></i> Itinéraire vers cette zone</button>
          <button type="button" id="btnSelectionEffacer" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:8px;"><i class="fa-solid fa-trash"></i> Effacer la sélection</button>'''
    contenu = contenu.replace(ancien_html, nouveau_html)

    # --- 7) Branchement du bouton btnSelectionItineraire ---
    ancien_wiring = "    onEvent('btnSelectionEffacer', 'click', effacerSelection);"
    if ancien_wiring not in contenu:
        raise SystemExit("ANCRE onEvent btnSelectionEffacer INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_wiring = ancien_wiring + '''
    onEvent('btnSelectionItineraire', 'click', function () {
      if (!formeSelectionActuelle) {
        definirAideSelection('Dessinez d\\'abord une zone de sélection.', '#b23b2e');
        return;
      }
      if (!userLatLng) {
        const status = document.getElementById('position-status');
        if (status) status.innerHTML = '<span style="color:#dc3545;"><i class="fa-solid fa-triangle-exclamation"></i> Clique d\\'abord sur « Me géolocaliser ».</span>';
        return;
      }
      const centre = turf.centroid(formeSelectionActuelle);
      const coords = centre.geometry.coordinates;
      calculerItineraire(coords[1], coords[0]);
    });'''
    contenu = contenu.replace(ancien_wiring, nouveau_wiring)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes (features 3/6 + 4/6 : selection enrichie + surlignage).")