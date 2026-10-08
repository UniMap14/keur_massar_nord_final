CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_html = '''          <label style="font-size:13px; font-weight:500; margin-top:8px; display:block;">Infrastructures</label>
          <div id="infraCategorieList"'''

nouveau_html = '''          <label style="font-size:13px; font-weight:500; margin-top:8px; display:block;">Infrastructures</label>
          <label style="display:flex; align-items:center; gap:7px; font-size:13px; cursor:pointer; margin-bottom:8px;">
            <input type="checkbox" id="toggle-cluster-infra" checked>
            <span>Regrouper (cluster)</span>
          </label>
          <div id="infraCategorieList"'''

if "toggle-cluster-infra" in contenu:
    print("DEJA FAIT : case a cocher deja presente.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    changements += 1
    print("OK : case a cocher 'Regrouper (cluster)' ajoutee.")
else:
    print("ERREUR : ancre HTML introuvable.")

ancien_js = '''  function afficherIconesInfrastructures(data) {
    if (coucheInfrastructures) map.removeLayer(coucheInfrastructures);
    coucheInfrastructures = L.markerClusterGroup({
      iconCreateFunction: creerIconeCluster,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
    });'''

nouveau_js = '''  let clusteringActif = true;

  function afficherIconesInfrastructures(data) {
    if (coucheInfrastructures) map.removeLayer(coucheInfrastructures);
    coucheInfrastructures = clusteringActif
      ? L.markerClusterGroup({
          iconCreateFunction: creerIconeCluster,
          maxClusterRadius: 50,
          spiderfyOnMaxZoom: true,
        })
      : L.layerGroup();'''

if "let clusteringActif" in contenu:
    print("DEJA FAIT : logique de bascule deja presente.")
elif ancien_js in contenu:
    contenu = contenu.replace(ancien_js, nouveau_js, 1)
    changements += 1
    print("OK : afficherIconesInfrastructures bascule maintenant entre cluster et icones individuelles.")
else:
    print("ERREUR : ancre JS introuvable.")

ancien_event = "    onEvent('filter-occupation', 'change', applyFilters);"
nouveau_event = '''    onEvent('filter-occupation', 'change', applyFilters);
    onEvent('toggle-cluster-infra', 'change', function (e) {
      clusteringActif = e.target.checked;
      afficherIconesInfrastructures(allParcelles);
    });'''

if "toggle-cluster-infra', 'change'" in contenu:
    print("DEJA FAIT : evenement deja branche.")
elif ancien_event in contenu:
    contenu = contenu.replace(ancien_event, nouveau_event, 1)
    changements += 1
    print("OK : evenement de bascule cluster/icones branche.")
else:
    print("ERREUR : ancre evenement introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")