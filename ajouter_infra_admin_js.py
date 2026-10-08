CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_apply = '''  function applyFilters() {
    const zoneFilter = document.getElementById('filter-zone').value;
    const statutSelect = document.getElementById('filter-statut');
    const statutFilter = statutSelect ? statutSelect.value : '';

    filtreFiscalActif = statutFilter;

    let filtered = allParcelles.features || [];
    if (zoneFilter) {
      filtered = filtered.filter(function (f) { return zoneLabelDe(f) === zoneFilter; });
    }
    if (statutFilter && statutFilter !== 'TOUS_COLORES') {
      filtered = filtered.filter(function (f) { return f.properties.statut_fiscal === statutFilter; });
    }

    filteredParcelles = filtered;
    redessinerCouches();
  }'''

nouveau_apply = '''  function applyFilters() {
    const statutSelect = document.getElementById('filter-statut');
    const statutFilter = statutSelect ? statutSelect.value : '';

    filtreFiscalActif = statutFilter;

    let filtered = allParcelles.features || [];
    if (statutFilter && statutFilter !== 'TOUS_COLORES') {
      filtered = filtered.filter(function (f) { return f.properties.statut_fiscal === statutFilter; });
    }

    filteredParcelles = filtered;
    redessinerCouches();
  }'''

if nouveau_apply in contenu:
    print("DEJA FAIT : applyFilters deja corrige.")
elif ancien_apply in contenu:
    contenu = contenu.replace(ancien_apply, nouveau_apply, 1)
    changements += 1
    print("OK : reference a filter-zone retiree d'applyFilters.")
else:
    print("ERREUR : ancre applyFilters introuvable.")

ancien_reinit = '''  function reinitialiserFiltres() {
    document.getElementById('filter-zone').value = '';
    const statutSelect = document.getElementById('filter-statut');
    if (statutSelect) statutSelect.value = '';
    document.getElementById('search-nicad').value = '';
    document.getElementById('search-result').textContent = '';
    filteredParcelles = [];
    filtreFiscalActif = '';
    redessinerCouches();
  }'''

nouveau_reinit = '''  function reinitialiserFiltres() {
    const statutSelect = document.getElementById('filter-statut');
    if (statutSelect) statutSelect.value = '';
    document.getElementById('search-nicad').value = '';
    document.getElementById('search-result').textContent = '';
    filteredParcelles = [];
    filtreFiscalActif = '';
    redessinerCouches();
  }'''

if nouveau_reinit in contenu:
    print("DEJA FAIT : reinitialiserFiltres deja corrige.")
elif ancien_reinit in contenu:
    contenu = contenu.replace(ancien_reinit, nouveau_reinit, 1)
    changements += 1
    print("OK : reference a filter-zone retiree de reinitialiserFiltres.")
else:
    print("ERREUR : ancre reinitialiserFiltres introuvable.")

ancien_event = "    onEvent('filter-zone', 'change', applyFilters);\n    onEvent('filter-statut', 'change', applyFilters);"
nouveau_event = "    onEvent('filter-statut', 'change', applyFilters);"

if nouveau_event in contenu and "onEvent('filter-zone'" not in contenu:
    print("DEJA FAIT : evenement filter-zone deja retire.")
elif ancien_event in contenu:
    contenu = contenu.replace(ancien_event, nouveau_event, 1)
    changements += 1
    print("OK : evenement filter-zone retire.")
else:
    print("ERREUR : ancre evenement introuvable.")

ancien_fn = "  function initMap() {"

nouveau_fn = '''  let coucheInfrastructuresAdmin = null;
  let categoriesInfraVues = {};
  let categoriesInfraActives = new Set();

  function collecterCategoriesInfra() {
    categoriesInfraVues = {};
    (allParcelles.features || []).forEach(function (f) {
      (f.properties.infrastructures || []).forEach(function (infra) {
        if (!categoriesInfraVues[infra.categorie]) {
          categoriesInfraVues[infra.categorie] = { couleur: infra.couleur, icone: infra.icone };
        }
      });
    });
  }

  function populateInfraFilter() {
    collecterCategoriesInfra();
    const conteneur = document.getElementById('infraCategorieList');
    if (!conteneur) return;
    conteneur.innerHTML = '';
    categoriesInfraActives = new Set(Object.keys(categoriesInfraVues));

    if (Object.keys(categoriesInfraVues).length === 0) {
      conteneur.innerHTML = '<div class="ep-empty" style="padding:10px 0;">Aucune infrastructure recensee.</div>';
      return;
    }

    Object.keys(categoriesInfraVues).sort().forEach(function (cat) {
      const info = categoriesInfraVues[cat];
      const div = document.createElement('div');
      div.className = 'control-toggle';
      div.innerHTML =
        '<label><input type="checkbox" class="infra-cat-checkbox" data-cat="' + cat + '" checked>' +
        '<span style="display:inline-flex; align-items:center; gap:6px;">' +
        '<span style="width:9px; height:9px; border-radius:50%; background:' + info.couleur + '; display:inline-block; flex-shrink:0;"></span>' +
        cat + '</span></label>';
      conteneur.appendChild(div);
    });

    conteneur.querySelectorAll('.infra-cat-checkbox').forEach(function (cb) {
      cb.addEventListener('change', function () {
        const cat = cb.getAttribute('data-cat');
        if (cb.checked) categoriesInfraActives.add(cat);
        else categoriesInfraActives.delete(cat);
        afficherIconesInfrastructures(allParcelles);
      });
    });
  }

  function afficherIconesInfrastructures(data) {
    if (coucheInfrastructuresAdmin) map.removeLayer(coucheInfrastructuresAdmin);
    coucheInfrastructuresAdmin = L.layerGroup();

    (data.features || []).forEach(function (feature) {
      (feature.properties.infrastructures || []).forEach(function (infra) {
        if (infra.latitude == null || infra.longitude == null) return;
        if (!categoriesInfraActives.has(infra.categorie)) return;

        const icone = L.divIcon({
          className: '',
          html:
            '<div style="background:' + (infra.couleur || '#7b3fa0') + '; width:22px; height:22px; ' +
            'border-radius:50%; border:2px solid white; box-shadow:0 1px 4px rgba(0,0,0,0.4); ' +
            'display:flex; align-items:center; justify-content:center;">' +
              '<i class="fa-solid ' + (infra.icone || 'fa-map-pin') + '" style="color:white; font-size:10px;"></i>' +
            '</div>',
          iconSize: [22, 22],
          iconAnchor: [11, 11],
        });

        L.marker([infra.latitude, infra.longitude], { icon: icone })
          .bindPopup('<strong>' + infra.nom + '</strong><br><span style="color:#766c5d;">' + infra.categorie + '</span>')
          .addTo(coucheInfrastructuresAdmin);
      });
    });

    coucheInfrastructuresAdmin.addTo(map);
  }

  function initMap() {'''

if "function afficherIconesInfrastructures" in contenu:
    print("DEJA FAIT : fonctions infrastructures deja presentes.")
elif ancien_fn in contenu:
    contenu = contenu.replace(ancien_fn, nouveau_fn, 1)
    changements += 1
    print("OK : fonctions d'affichage/filtre des infrastructures ajoutees.")
else:
    print("ERREUR : ancre initMap introuvable.")

ancien_load = '''        allParcelles = data;
        redessinerCouches();
        populateZoneFilter();
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {'''

nouveau_load = '''        allParcelles = data;
        redessinerCouches();
        populateInfraFilter();
        afficherIconesInfrastructures(data);
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {'''

if nouveau_load in contenu:
    print("DEJA FAIT : loadParcelles deja corrige.")
elif ancien_load in contenu:
    contenu = contenu.replace(ancien_load, nouveau_load, 1)
    changements += 1
    print("OK : loadParcelles affiche maintenant les infrastructures.")
else:
    print("ERREUR : ancre loadParcelles introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 2/3 : JS). ===")