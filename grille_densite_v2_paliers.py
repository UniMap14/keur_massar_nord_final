FICHIERS = [
    "foncier/templates/foncier/geoportail.html",
    "foncier/templates/foncier/geoportail_admin.html",
]

ancien_fonctions = '''  function couleurDensite(t) {
    const r = Math.round(255 + (178 - 255) * t);
    const g = Math.round(255 + (59 - 255) * t);
    const b = Math.round(255 + (46 - 255) * t);
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  function afficherGrilleDensite(infras) {
    if (coucheChaleur) { map.removeLayer(coucheChaleur); coucheChaleur = null; }
    if (!infras || infras.length === 0) return;

    const bounds = (coucheParcelles && coucheParcelles.getBounds().isValid()) ? coucheParcelles.getBounds() : map.getBounds();
    const pas = 0.0025;

    const compteurs = {};
    let maxCompte = 0;
    infras.forEach(function (infra) {
      const cy = Math.floor(infra.latitude / pas);
      const cx = Math.floor(infra.longitude / pas);
      const cle = cy + '_' + cx;
      compteurs[cle] = (compteurs[cle] || 0) + 1;
      if (compteurs[cle] > maxCompte) maxCompte = compteurs[cle];
    });

    const groupe = L.layerGroup();
    for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += pas) {
      for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += pas) {
        const cy = Math.floor(lat / pas);
        const cx = Math.floor(lng / pas);
        const cle = cy + '_' + cx;
        const n = compteurs[cle] || 0;
        if (n === 0) continue;
        const intensite = Math.min(n / Math.max(maxCompte, 1), 1);
        L.rectangle(
          [[lat, lng], [lat + pas, lng + pas]],
          { color: 'transparent', fillColor: couleurDensite(intensite), fillOpacity: 0.6, weight: 0 }
        ).addTo(groupe);
      }
    }
    coucheChaleur = groupe;
    coucheChaleur.addTo(map);
  }'''

nouveau_fonctions = '''  const PALIERS_DENSITE = [
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
  }

  function afficherLegendeDensite(maxCompte) {
    const conteneur = document.getElementById('legendeDensite');
    if (!conteneur) return;
    if (!maxCompte) { conteneur.style.display = 'none'; return; }

    const seuil1 = Math.max(1, Math.ceil(maxCompte * 0.25));
    const seuil2 = Math.max(seuil1 + 1, Math.ceil(maxCompte * 0.5));
    const seuil3 = Math.max(seuil2 + 1, Math.ceil(maxCompte * 0.75));

    conteneur.innerHTML =
      '<div style="font-size:11px; font-weight:700; color:#3c2a20; margin-bottom:6px;">Densité (nb. infra / case)</div>' +
      '<div style="display:flex; align-items:center; gap:6px; font-size:11px; margin-bottom:3px;"><span style="width:14px; height:14px; background:#ffffff; border:1px solid #999; display:inline-block;"></span> 0</div>' +
      '<div style="display:flex; align-items:center; gap:6px; font-size:11px; margin-bottom:3px;"><span style="width:14px; height:14px; background:#f6c6bd; border:1px solid #999; display:inline-block;"></span> 1 – ' + seuil1 + '</div>' +
      '<div style="display:flex; align-items:center; gap:6px; font-size:11px; margin-bottom:3px;"><span style="width:14px; height:14px; background:#ea7a68; border:1px solid #999; display:inline-block;"></span> ' + (seuil1+1) + ' – ' + seuil2 + '</div>' +
      '<div style="display:flex; align-items:center; gap:6px; font-size:11px; margin-bottom:3px;"><span style="width:14px; height:14px; background:#d43a2a; border:1px solid #999; display:inline-block;"></span> ' + (seuil2+1) + ' – ' + seuil3 + '</div>' +
      '<div style="display:flex; align-items:center; gap:6px; font-size:11px;"><span style="width:14px; height:14px; background:#8f1d10; border:1px solid #999; display:inline-block;"></span> ' + (seuil3+1) + ' et +</div>';
    conteneur.style.display = 'block';
  }

  function afficherGrilleDensite(infras) {
    if (coucheChaleur) { map.removeLayer(coucheChaleur); coucheChaleur = null; }
    afficherLegendeDensite(0);
    if (!infras || infras.length === 0) return;

    const bounds = (coucheParcelles && coucheParcelles.getBounds().isValid()) ? coucheParcelles.getBounds() : map.getBounds();
    const pas = 0.0045;

    const compteurs = {};
    let maxCompte = 0;
    infras.forEach(function (infra) {
      const cy = Math.floor(infra.latitude / pas);
      const cx = Math.floor(infra.longitude / pas);
      const cle = cy + '_' + cx;
      compteurs[cle] = (compteurs[cle] || 0) + 1;
      if (compteurs[cle] > maxCompte) maxCompte = compteurs[cle];
    });

    const groupe = L.layerGroup();
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
    }
    coucheChaleur = groupe;
    coucheChaleur.addTo(map);
    afficherLegendeDensite(maxCompte);
  }'''

CSS_LABEL = '''  .grille-densite-label {
    background: transparent !important; border: none !important; box-shadow: none !important;
    font-size: 11px !important; font-weight: 700 !important; color: #2b1e16 !important;
  }
  .grille-densite-label::before { display: none !important; }
  #legendeDensite {
    position: absolute; top: 14px; left: 14px; z-index: 1100; display: none;
    background: rgba(255,255,255,0.97); border: 1px solid #e6ded0; border-radius: 10px;
    padding: 10px 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.12);
  }
'''

for chemin in FICHIERS:
    try:
        with open(chemin, encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"IGNORE : {chemin} introuvable.")
        continue

    resultats = []

    if "PALIERS_DENSITE" in contenu:
        resultats.append("fonctions deja mises a jour (v2)")
    elif ancien_fonctions in contenu:
        contenu = contenu.replace(ancien_fonctions, nouveau_fonctions, 1)
        resultats.append("fonctions remplacees par la version a paliers")
    else:
        resultats.append("ERREUR : fonctions v1 introuvables (as-tu deja lance le 1er script ?)")

    if "grille-densite-label" in contenu and "<style>" in contenu:
        if ".grille-densite-label {" in contenu:
            resultats.append("CSS deja present")
        else:
            contenu = contenu.replace("<style>", "<style>\n" + CSS_LABEL, 1)
            resultats.append("CSS ajoute")
    elif "<style>" in contenu:
        contenu = contenu.replace("<style>", "<style>\n" + CSS_LABEL, 1)
        resultats.append("CSS ajoute")
    else:
        resultats.append("ERREUR : balise <style> introuvable")

    if 'id="legendeDensite"' in contenu:
        resultats.append("conteneur legende deja present")
    elif '<div id="mapLoader" class="map-loader">' in contenu:
        contenu = contenu.replace(
            '<div id="mapLoader" class="map-loader">',
            '<div id="legendeDensite"></div>\n      <div id="mapLoader" class="map-loader">',
            1,
        )
        resultats.append("conteneur legende ajoute")
    else:
        resultats.append("ERREUR : point d'insertion de la legende introuvable")

    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)

    print(f"{chemin} : " + " | ".join(resultats))