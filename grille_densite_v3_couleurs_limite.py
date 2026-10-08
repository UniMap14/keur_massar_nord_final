FICHIERS = [
    "foncier/templates/foncier/geoportail.html",
    "foncier/templates/foncier/geoportail_admin.html",
]

ancien_paliers = '''  const PALIERS_DENSITE = [
    { max: 0, couleur: '#ffffff', label: '0' },
    { max: 0.25, couleur: '#f6c6bd', label: 'Faible' },
    { max: 0.5, couleur: '#ea7a68', label: 'Moyen' },
    { max: 0.75, couleur: '#d43a2a', label: 'Élevé' },
    { max: 1, couleur: '#8f1d10', label: 'Très élevé' },
  ];

  function couleurPalier(n, maxCompte) {
    if (n === 0) return PALIERS_DENSITE[0].couleur;
    const ratio = n / Math.max(maxCompte, 1);
    if (ratio <= 0.25) return PALIERS_DENSITE[1].couleur;
    if (ratio <= 0.5) return PALIERS_DENSITE[2].couleur;
    if (ratio <= 0.75) return PALIERS_DENSITE[3].couleur;
    return PALIERS_DENSITE[4].couleur;
  }'''

nouveau_paliers = '''  const PALIERS_DENSITE = [
    { max: 0, couleur: '#ffffff', label: '0' },
    { max: 0.25, couleur: '#e8958a', label: 'Faible' },
    { max: 0.5, couleur: '#d94a3a', label: 'Moyen' },
    { max: 0.75, couleur: '#a11d12', label: 'Élevé' },
    { max: 1, couleur: '#5c0f08', label: 'Très élevé' },
  ];

  function couleurPalier(n, maxCompte) {
    if (n === 0) return PALIERS_DENSITE[0].couleur;
    const ratio = n / Math.max(maxCompte, 1);
    if (ratio <= 0.25) return PALIERS_DENSITE[1].couleur;
    if (ratio <= 0.5) return PALIERS_DENSITE[2].couleur;
    if (ratio <= 0.75) return PALIERS_DENSITE[3].couleur;
    return PALIERS_DENSITE[4].couleur;
  }

  function celluleDansLaCommune(latCentre, lngCentre) {
    if (!allLimites || !allLimites.features || allLimites.features.length === 0) return true;
    if (typeof turf === 'undefined') return true;
    const point = turf.point([lngCentre, latCentre]);
    for (let i = 0; i < allLimites.features.length; i++) {
      try {
        if (turf.booleanPointInPolygon(point, allLimites.features[i])) return true;
      } catch (e) { /* geometrie invalide, on ignore cette entite */ }
    }
    return false;
  }'''

ancien_boucle = '''    const groupe = L.layerGroup();
    for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += pas) {
      for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += pas) {
        const cy = Math.floor(lat / pas);
        const cx = Math.floor(lng / pas);
        const cle = cy + '_' + cx;
        const n = compteurs[cle] || 0;

        const rect = L.rectangle(
          [[lat, lng], [lat + pas, lng + pas]],
          { color: '#8a8276', weight: 1, fillColor: couleurPalier(n, maxCompte), fillOpacity: 0.75 }
        );
        rect.bindTooltip(String(n), {
          permanent: true, direction: 'center', className: 'grille-densite-label', interactive: false,
        });
        rect.addTo(groupe);
      }
    }'''

nouveau_boucle = '''    const groupe = L.layerGroup();
    for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += pas) {
      for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += pas) {
        const centreLat = lat + pas / 2;
        const centreLng = lng + pas / 2;
        if (!celluleDansLaCommune(centreLat, centreLng)) continue;

        const cy = Math.floor(lat / pas);
        const cx = Math.floor(lng / pas);
        const cle = cy + '_' + cx;
        const n = compteurs[cle] || 0;

        const rect = L.rectangle(
          [[lat, lng], [lat + pas, lng + pas]],
          { color: '#8a8276', weight: 1, fillColor: couleurPalier(n, maxCompte), fillOpacity: 0.75 }
        );
        rect.bindTooltip(String(n), {
          permanent: true, direction: 'center', className: 'grille-densite-label', interactive: false,
        });
        rect.addTo(groupe);
      }
    }'''

for chemin in FICHIERS:
    try:
        with open(chemin, encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"IGNORE : {chemin} introuvable.")
        continue

    resultats = []

    if "'#5c0f08'" in contenu:
        resultats.append("couleurs deja assombries")
    elif ancien_paliers in contenu:
        contenu = contenu.replace(ancien_paliers, nouveau_paliers, 1)
        resultats.append("couleurs assombries + fonction de decoupage ajoutee")
    else:
        resultats.append("ERREUR : bloc paliers introuvable (as-tu lance le script precedent d'abord ?)")

    if "celluleDansLaCommune(centreLat, centreLng)" in contenu:
        resultats.append("decoupage deja applique a la boucle")
    elif ancien_boucle in contenu:
        contenu = contenu.replace(ancien_boucle, nouveau_boucle, 1)
        resultats.append("decoupage applique a la boucle de la grille")
    else:
        resultats.append("ERREUR : boucle de grille introuvable")

    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)

    print(f"{chemin} : " + " | ".join(resultats))