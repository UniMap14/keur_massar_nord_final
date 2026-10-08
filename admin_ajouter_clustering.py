CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_script = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>'

nouveau_script = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js"></script>'''

if "leaflet.markercluster" in contenu:
    print("DEJA FAIT : scripts de clustering deja presents.")
elif ancien_script in contenu:
    contenu = contenu.replace(ancien_script, nouveau_script, 1)
    changements += 1
    print("OK : scripts/CSS du plugin de clustering ajoutes.")
else:
    print("ERREUR : ancre script introuvable.")

ancien_fn = '''  function afficherIconesInfrastructures(data) {
    if (coucheInfrastructuresAdmin) map.removeLayer(coucheInfrastructuresAdmin);
    coucheInfrastructuresAdmin = L.layerGroup();'''

nouveau_fn = '''  function creerIconeCluster(cluster) {
    const nombre = cluster.getChildCount();
    let taille = 34;
    if (nombre >= 50) taille = 46;
    else if (nombre >= 10) taille = 40;
    return L.divIcon({
      html: '<div style="background:#c9982e; color:#3c2a20; width:' + taille + 'px; height:' + taille + 'px; ' +
        'border-radius:50%; border:3px solid white; box-shadow:0 2px 8px rgba(0,0,0,0.35); ' +
        'display:flex; align-items:center; justify-content:center; font-weight:700; font-size:' + (taille > 40 ? '14px' : '12.5px') + ';">' +
        nombre + '</div>',
      className: '',
      iconSize: [taille, taille],
    });
  }

  function afficherIconesInfrastructures(data) {
    if (coucheInfrastructuresAdmin) map.removeLayer(coucheInfrastructuresAdmin);
    coucheInfrastructuresAdmin = L.markerClusterGroup({
      iconCreateFunction: creerIconeCluster,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
    });'''

if "function creerIconeCluster" in contenu:
    print("DEJA FAIT : clustering deja applique.")
elif ancien_fn in contenu:
    contenu = contenu.replace(ancien_fn, nouveau_fn, 1)
    changements += 1
    print("OK : afficherIconesInfrastructures utilise maintenant le clustering.")
else:
    print("ERREUR : ancre afficherIconesInfrastructures introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")