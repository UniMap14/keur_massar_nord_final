CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    coucheInfrastructures = clusteringActif
      ? L.markerClusterGroup({
          iconCreateFunction: creerIconeCluster,
          maxClusterRadius: 50,
          spiderfyOnMaxZoom: true,
        })
      : L.layerGroup();'''

nouveau = "    coucheInfrastructures = L.layerGroup();"

if nouveau in contenu and "markerClusterGroup" not in contenu:
    print("DEJA FAIT : clustering deja retire.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : clustering retire, retour aux icones individuelles.")
else:
    print("ERREUR : bloc exact introuvable.")