CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''  function styleParcelle(feature) {
    const estSelectionnee = idDeFeature(feature) === idDeFeature(selectedFeature);
    const aUneInfrastructure = feature.properties.infrastructures && feature.properties.infrastructures.length > 0;

    if (estSelectionnee) {
      return {
        renderer: renduCanvas,
        color: '#2f7a4f',
        weight: 2,
        fillColor: '#2f7a4f',
        fillOpacity: 0.7,
      };
    }
    if (aUneInfrastructure) {
      return {
        renderer: renduCanvas,
        color: '#7b3fa0',
        weight: 1.5,
        fillColor: '#7b3fa0',
        fillOpacity: 0.55,
      };
    }
    return {
      renderer: renduCanvas,
      color: '#c9982e',
      weight: 1,
      fillColor: '#c9982e',
      fillOpacity: 0.35,
    };
  }'''

nouveau = '''  function styleParcelle(feature) {
    const estSelectionnee = idDeFeature(feature) === idDeFeature(selectedFeature);
    const infras = feature.properties.infrastructures;
    const aUneInfrastructure = infras && infras.length > 0;

    if (estSelectionnee) {
      return {
        renderer: renduCanvas,
        color: '#2f7a4f',
        weight: 2,
        fillColor: '#2f7a4f',
        fillOpacity: 0.7,
      };
    }
    if (aUneInfrastructure) {
      const couleurCategorie = infras[0].couleur || '#7b3fa0';
      return {
        renderer: renduCanvas,
        color: couleurCategorie,
        weight: 1.5,
        fillColor: couleurCategorie,
        fillOpacity: 0.30,
      };
    }
    return {
      renderer: renduCanvas,
      color: '#c9982e',
      weight: 1,
      fillColor: '#c9982e',
      fillOpacity: 0.35,
    };
  }'''

if "couleurCategorie" in contenu:
    print("DEJA FAIT : deja modifie.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : styleParcelle utilise maintenant la couleur reelle de la categorie.")
else:
    print("ERREUR : bloc exact introuvable.")