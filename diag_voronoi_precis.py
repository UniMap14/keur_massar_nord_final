# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

ancien_voronoi = '''  function basculerVoronoi(active) {
    if (coucheVoronoi) { map.removeLayer(coucheVoronoi); coucheVoronoi = null; }
    const resultEl = document.getElementById('voronoiResult');
    if (!active) { resultEl.textContent = ''; return; }
    if (typeof turf === 'undefined') { resultEl.innerHTML = '<span style="color:#b23b2e;">BibliothèqueTurf.js indisponible.</span>'; return; }

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

idx = contenu.find("function basculerVoronoi(active)")
if idx == -1:
    print("Motif de base introuvable du tout !")
else:
    debut = contenu.rfind("\n", 0, idx) + 1
    segment_reel = contenu[debut:debut+len(ancien_voronoi)]
    if segment_reel == ancien_voronoi:
        print("IDENTIQUE - bizarre, ca devrait marcher.")
    else:
        print("DIFFERENCE TROUVEE.")
        for i, (a, b) in enumerate(zip(ancien_voronoi, segment_reel)):
            if a != b:
                print(f"Position {i}: attendu {repr(a)} ({ord(a)}) vs reel {repr(b)} ({ord(b)})")
                print("Contexte attendu:", repr(ancien_voronoi[max(0,i-40):i+40]))
                print("Contexte reel   :", repr(segment_reel[max(0,i-40):i+40]))
                break
        else:
            print("Meme contenu jusqu'a la longueur min, mais longueurs differentes:")
            print("longueur attendue:", len(ancien_voronoi), "longueur reelle:", len(segment_reel))