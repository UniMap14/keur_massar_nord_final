CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_afficher = '''  function afficherIconesInfrastructures(data) {
    if (coucheInfrastructures) map.removeLayer(coucheInfrastructures);
    coucheInfrastructures = L.layerGroup();

    (data.features || []).forEach(function (feature) {
      const infras = feature.properties.infrastructures || [];
      infras.forEach(function (infra) {
        if (infra.latitude == null || infra.longitude == null) return;'''

nouveau_afficher = '''  let categoriesInfraVues = {};
  let categoriesInfraActives = new Set();

  function populateInfraFilter() {
    categoriesInfraVues = {};
    (allParcelles.features || []).forEach(function (f) {
      (f.properties.infrastructures || []).forEach(function (infra) {
        if (!categoriesInfraVues[infra.categorie]) {
          categoriesInfraVues[infra.categorie] = { couleur: infra.couleur, icone: infra.icone };
        }
      });
    });

    const conteneur = document.getElementById('infraCategorieList');
    if (!conteneur) return;
    conteneur.innerHTML = '';
    categoriesInfraActives = new Set(Object.keys(categoriesInfraVues));

    if (Object.keys(categoriesInfraVues).length === 0) {
      conteneur.innerHTML = '<div style="font-size:12px; color:#766c5d;">Aucune infrastructure recensee.</div>';
      return;
    }

    Object.keys(categoriesInfraVues).sort().forEach(function (cat) {
      const info = categoriesInfraVues[cat];
      const label = document.createElement('label');
      label.style.cssText = 'display:flex; align-items:center; gap:7px; font-size:13px; cursor:pointer;';
      label.innerHTML =
        '<input type="checkbox" class="infra-cat-checkbox" data-cat="' + cat + '" checked>' +
        '<span style="width:9px; height:9px; border-radius:50%; background:' + info.couleur + '; display:inline-block; flex-shrink:0;"></span>' +
        '<span>' + cat + '</span>';
      conteneur.appendChild(label);
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
    if (coucheInfrastructures) map.removeLayer(coucheInfrastructures);
    coucheInfrastructures = L.layerGroup();

    (data.features || []).forEach(function (feature) {
      const infras = feature.properties.infrastructures || [];
      infras.forEach(function (infra) {
        if (infra.latitude == null || infra.longitude == null) return;
        if (!categoriesInfraActives.has(infra.categorie)) return;'''

if "function populateInfraFilter" in contenu:
    print("DEJA FAIT : populateInfraFilter deja present.")
elif ancien_afficher in contenu:
    contenu = contenu.replace(ancien_afficher, nouveau_afficher, 1)
    changements += 1
    print("OK : filtre par categorie ajoute a afficherIconesInfrastructures.")
else:
    print("ERREUR : ancre afficherIconesInfrastructures introuvable.")

ancien_load = '''        allParcelles = data;
        redessinerCouches();
        populateZoneFilter();
        populateOccupationFilter();'''

nouveau_load = '''        allParcelles = data;
        redessinerCouches();
        populateInfraFilter();
        populateOccupationFilter();'''

if nouveau_load in contenu:
    print("DEJA FAIT : loadParcelles deja corrige.")
elif ancien_load in contenu:
    contenu = contenu.replace(ancien_load, nouveau_load, 1)
    changements += 1
    print("OK : loadParcelles utilise maintenant populateInfraFilter.")
else:
    print("ERREUR : ancre loadParcelles introuvable.")

ancien_url = '''    document.getElementById('search-nicad').value = q;

    const zoneSelect = document.getElementById('filter-zone');
    const zoneMatch = Array.from(zoneSelect.options).find(function (opt) {
      return opt.value.toLowerCase() === q.toLowerCase();
    });

    if (zoneMatch) {
      zoneSelect.value = zoneMatch.value;
      applyFilters();
      if (filteredParcelles.length) {
        const coucheTemp = L.geoJSON(filteredParcelles);
        map.fitBounds(coucheTemp.getBounds(), { padding: [50, 50] });
      }
    } else {
      searchParcelle();
    }
  }'''

nouveau_url = '''    document.getElementById('search-nicad').value = q;
    searchParcelle();
  }'''

if nouveau_url in contenu:
    print("DEJA FAIT : appliquerRechercheDepuisURL deja corrige.")
elif ancien_url in contenu:
    contenu = contenu.replace(ancien_url, nouveau_url, 1)
    changements += 1
    print("OK : appliquerRechercheDepuisURL simplifie (recherche NICAD directe).")
else:
    print("ERREUR : ancre appliquerRechercheDepuisURL introuvable.")

ancien_apply = '''  function applyFilters() {
    const zoneFilter = document.getElementById('filter-zone').value;
    const occupationFilter = document.getElementById('filter-occupation').value;

    let filtered = allParcelles.features || [];
    if (zoneFilter) {
      filtered = filtered.filter(function (f) { return zoneLabelDe(f) === zoneFilter; });
    }
    if (occupationFilter) {'''

nouveau_apply = '''  function applyFilters() {
    const occupationFilter = document.getElementById('filter-occupation').value;

    let filtered = allParcelles.features || [];
    if (occupationFilter) {'''

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
    document.getElementById('filter-occupation').value = '';'''

nouveau_reinit = '''  function reinitialiserFiltres() {
    document.getElementById('filter-occupation').value = '';'''

if nouveau_reinit in contenu:
    print("DEJA FAIT : reinitialiserFiltres deja corrige.")
elif ancien_reinit in contenu:
    contenu = contenu.replace(ancien_reinit, nouveau_reinit, 1)
    changements += 1
    print("OK : reference a filter-zone retiree de reinitialiserFiltres.")
else:
    print("ERREUR : ancre reinitialiserFiltres introuvable.")

ancien_event = "    onEvent('filter-zone', 'change', applyFilters);\n    onEvent('filter-occupation', 'change', applyFilters);"
nouveau_event = "    onEvent('filter-occupation', 'change', applyFilters);"

if nouveau_event in contenu and "onEvent('filter-zone'" not in contenu:
    print("DEJA FAIT : evenement filter-zone deja retire.")
elif ancien_event in contenu:
    contenu = contenu.replace(ancien_event, nouveau_event, 1)
    changements += 1
    print("OK : evenement filter-zone retire.")
else:
    print("ERREUR : ancre evenement introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 2/2 : JS). ===")