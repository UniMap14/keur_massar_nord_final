# -*- coding: utf-8 -*-
"""
Ameliore l'outil "Selection spatiale" du geoportail public :
  1) Respecte le filtre actif (recherche NICAD / occupation du sol /
     quartier) au lieu de toujours balayer toutes les parcelles.
  2) Affiche les quartiers couverts par la forme dessinee.
  3) Affiche les infrastructures situees dans la zone dessinee.
  4) Ajoute un bouton "Itineraire vers cette zone" (centre de la forme).

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "btnSelectionItineraire"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) HTML du panneau : ajoute selZones, selInfraSection, bouton itineraire ---
    ancien_html = '''          <div id="selOccupation" class="geo-tool-result" style="color:#766c5d;"></div>
          <div id="selection-liste" class="geo-selection-liste"></div>
          <div style="display:flex; gap:8px; margin-top:10px;">
            <button type="button" id="btnSelectionCSV" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-file-csv"></i> CSV</button>
            <button type="button" id="btnSelectionGeoJSON" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-map"></i> GeoJSON</button>
          </div>
          <button type="button" id="btnSelectionEffacer" class="geo-btn geo-btn-ghost geo-btn-block" style="margin-top:8px;"><i class="fa-solid fa-trash"></i> Effacer la sélection</button>'''
    if ancien_html not in contenu:
        raise SystemExit("ANCRE HTML panneau selection INTROUVABLE - abandon, rien n'a ete modifie.")

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

    # --- 2) Variables globales supplementaires ---
    ancienne_var = "  let selectionSet = new Set();"
    if ancienne_var not in contenu:
        raise SystemExit("ANCRE 'selectionSet' INTROUVABLE - abandon partiel, verifie le fichier.")
    nouvelle_var = (
        ancienne_var + "\n"
        "  let formeSelectionActuelle = null;\n"
        "  let selectionZones = [];\n"
        "  let selectionInfra = [];"
    )
    contenu = contenu.replace(ancienne_var, nouvelle_var)

    # --- 3) Memoriser la derniere forme dessinee ---
    ancien_appel_calcul = "    calculerSelection(forme);"
    if ancien_appel_calcul not in contenu:
        raise SystemExit("ANCRE 'calculerSelection(forme)' INTROUVABLE - abandon partiel, verifie le fichier.")
    nouvel_appel_calcul = "    formeSelectionActuelle = forme;\n    calculerSelection(forme);"
    contenu = contenu.replace(ancien_appel_calcul, nouvel_appel_calcul)

    # --- 4) calculerSelection : respecte le filtre actif + calcule zones/infra ---
    ancien_calcul = '''      const bb = turf.bbox(forme);
      const trouvees = [];
      (allParcelles.features || []).forEach(function (f) {
        if (!f.geometry) return;
        let b = cacheBbox.get(f);
        if (!b) { b = turf.bbox(f); cacheBbox.set(f, b); }
        if (b[0] > bb[2] || b[2] < bb[0] || b[1] > bb[3] || b[3] < bb[1]) return;
        try { if (turf.booleanIntersects(f, forme)) trouvees.push(f); } catch (err) {}
      });
      selectionFeatures = trouvees;
      selectionSet = new Set(trouvees);'''
    if ancien_calcul not in contenu:
        raise SystemExit("ANCRE corps calculerSelection INTROUVABLE - abandon partiel, verifie le fichier.")

    nouveau_calcul = '''      const bb = turf.bbox(forme);
      const trouvees = [];
      const baseParcelles = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);
      baseParcelles.forEach(function (f) {
        if (!f.geometry) return;
        let b = cacheBbox.get(f);
        if (!b) { b = turf.bbox(f); cacheBbox.set(f, b); }
        if (b[0] > bb[2] || b[2] < bb[0] || b[1] > bb[3] || b[3] < bb[1]) return;
        try { if (turf.booleanIntersects(f, forme)) trouvees.push(f); } catch (err) {}
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
      selectionSet = new Set(trouvees);'''
    contenu = contenu.replace(ancien_calcul, nouveau_calcul)

    # --- 5) afficherResultatSelection : affiche zones + infra ---
    ancien_affichage = '''    document.getElementById('selOccupation').textContent = Object.keys(compteOcc)
      .sort(function (a, b) { return compteOcc[b] - compteOcc[a]; }).slice(0, 3)
      .map(function (o) { return o + ' : ' + compteOcc[o]; }).join(' · ');'''
    if ancien_affichage not in contenu:
        raise SystemExit("ANCRE affichage selOccupation INTROUVABLE - abandon partiel, verifie le fichier.")

    nouvel_affichage = ancien_affichage + '''

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
          return '<div class="geo-selection-item"><span class="nom">' + echapperHtml(i.nom || 'Infrastructure') + '</span></div>';
        }).join('');
        sectionInfra.style.display = 'block';
      } else {
        listeInfra.innerHTML = '';
        sectionInfra.style.display = 'none';
      }
    }'''
    contenu = contenu.replace(ancien_affichage, nouvel_affichage)

    # --- 6) effacerSelection : reinitialise les nouvelles variables ---
    ancien_effacer = '''    if (coucheFormeSelection) { map.removeLayer(coucheFormeSelection); coucheFormeSelection = null; }
    selectionFeatures = [];
    selectionSet = new Set();'''
    if ancien_effacer not in contenu:
        raise SystemExit("ANCRE effacerSelection INTROUVABLE - abandon partiel, verifie le fichier.")
    nouvel_effacer = ancien_effacer + '''
    formeSelectionActuelle = null;
    selectionZones = [];
    selectionInfra = [];'''
    contenu = contenu.replace(ancien_effacer, nouvel_effacer)

    # --- 7) Branchement du bouton "Itineraire vers cette zone" ---
    ancien_bouton = "    onEvent('btnSelectionEffacer', 'click', effacerSelection);"
    if ancien_bouton not in contenu:
        raise SystemExit("ANCRE onEvent btnSelectionEffacer INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_bouton = ancien_bouton + '''
    onEvent('btnSelectionItineraire', 'click', function () {
      if (!formeSelectionActuelle) {
        definirAideSelection('Dessinez d\\'abord une zone de sélection.', '#b23b2e');
        return;
      }
      if (!userLatLng) {
        const status = document.getElementById('position-status');
        if (status) status.innerHTML = '<span style="color:#dc3545;"><i class="fa-solid fa-triangle-exclamation"></i> Clique d\\'abord sur \\u00ab Me g\\u00e9olocaliser \\u00bb.</span>';
        return;
      }
      const centre = turf.centroid(formeSelectionActuelle);
      const coords = centre.geometry.coordinates;
      calculerItineraire(coords[1], coords[0]);
    });'''
    contenu = contenu.replace(ancien_bouton, nouveau_bouton)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")