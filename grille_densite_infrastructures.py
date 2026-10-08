FICHIERS = [
    "foncier/templates/foncier/geoportail.html",
    "foncier/templates/foncier/geoportail_admin.html",
]

ancien_var = '''  let coucheChaleur = null;
  let modeChaleurActif = false;
  let dernieresDonneesInfra = null;'''

nouveau_var = '''  let coucheChaleur = null;
  let modeChaleurActif = false;
  let dernieresDonneesInfra = null;

  function couleurDensite(t) {
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

ancien_bascule = '''    if (modeChaleurActif) {
      const points = infrasAffichees.map(function (infra) { return [infra.latitude, infra.longitude, 1]; });
      coucheChaleur = L.heatLayer(points, { radius: 35, blur: 25, minOpacity: 0.2, max: 1.5, maxZoom: 17, gradient: { 0.2: '#3468a8', 0.5: '#c9982e', 0.8: '#b23b2e' } });
      coucheChaleur.addTo(map);
    } else {
      coucheInfrastructures.addTo(map);
    }'''

nouveau_bascule = '''    if (modeChaleurActif) {
      afficherGrilleDensite(infrasAffichees);
    } else {
      coucheInfrastructures.addTo(map);
    }'''

ancien_label = '''        <label class="geo-layer-item" style="margin-top:10px;">
          <input type="checkbox" id="toggle-carte-chaleur">
          <span>Carte de chaleur (densité)</span>
        </label>'''

nouveau_label = '''        <label class="geo-layer-item" style="margin-top:10px;">
          <input type="checkbox" id="toggle-carte-chaleur">
          <span>Grille de densité (mailles)</span>
        </label>'''

# variante avec indentation differente (panneau "Couches d'infrastructures" de l'admin)
ancien_label_alt = '''        <label class="geo-layer-item" style="margin-bottom:10px;">
          <input type="checkbox" id="toggle-carte-chaleur">
          <span>Carte de chaleur (densité)</span>
        </label>'''

nouveau_label_alt = '''        <label class="geo-layer-item" style="margin-bottom:10px;">
          <input type="checkbox" id="toggle-carte-chaleur">
          <span>Grille de densité (mailles)</span>
        </label>'''

for chemin in FICHIERS:
    try:
        with open(chemin, encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"IGNORE : {chemin} introuvable.")
        continue

    resultats = []

    if "function afficherGrilleDensite" in contenu:
        resultats.append("CSS/JS grille deja present")
    elif ancien_var in contenu:
        contenu = contenu.replace(ancien_var, nouveau_var, 1)
        resultats.append("fonctions grille ajoutees")
    else:
        resultats.append("ERREUR bloc variables introuvable")

    if "afficherGrilleDensite(infrasAffichees);" in contenu:
        resultats.append("bascule deja mise a jour")
    elif ancien_bascule in contenu:
        contenu = contenu.replace(ancien_bascule, nouveau_bascule, 1)
        resultats.append("bascule mise a jour")
    else:
        resultats.append("ERREUR bloc bascule introuvable")

    if "Grille de densité (mailles)" in contenu:
        resultats.append("libelle deja change")
    elif ancien_label in contenu:
        contenu = contenu.replace(ancien_label, nouveau_label, 1)
        resultats.append("libelle change")
    elif ancien_label_alt in contenu:
        contenu = contenu.replace(ancien_label_alt, nouveau_label_alt, 1)
        resultats.append("libelle change (variante)")
    else:
        resultats.append("ERREUR libelle introuvable")

    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)

    print(f"{chemin} : " + " | ".join(resultats))