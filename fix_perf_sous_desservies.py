# -*- coding: utf-8 -*-
"""
Accelere l'analyse "Zones sous-desservies" du geoportail public.

Cause reelle de la lenteur : pour CHAQUE cellule de la grille ET pour
CHAQUE parcelle (jusqu'a 40000+), le code comparait la distance a TOUTES
les infrastructures (243) une par une -- jusqu'a ~9,9 millions de calculs
de distance rien que pour la partie "parcelles concernees". On ajoute un
index spatial (grille) des infrastructures : chaque cellule/parcelle ne
compare plus qu'aux quelques infrastructures proches, au lieu de toutes.
Le resultat est identique, juste beaucoup plus rapide.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_perf_sous_desservies.py
"""
import os

CHEMIN = os.path.join("foncier", "templates", "foncier", "geoportail.html")

if not os.path.exists(CHEMIN):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN}")

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

PATCHES = []

# A) Fonctions utilitaires d'index spatial, inserees juste avant
#    analyserZonesSousDesservies.
PATCHES.append((
    "helpers index spatial",
    """  // ===== Zones sous-desservies =====
  let coucheSousDesservis = null;

  function analyserZonesSousDesservies() {""",
    """  // ===== Index spatial des infrastructures (recherche rapide du plus
  //       proche voisin), utilise par l'analyse "zones sous-desservies" =====
  function construireIndexInfra(infras, tailleCelluleDeg) {
    const index = new Map();
    infras.forEach(function (infra, i) {
      const cx = Math.floor(infra.longitude / tailleCelluleDeg);
      const cy = Math.floor(infra.latitude / tailleCelluleDeg);
      const cle = cx + ',' + cy;
      if (!index.has(cle)) index.set(cle, []);
      index.get(cle).push(i);
    });
    return index;
  }

  function distanceMinIndexee(lat, lng, infras, index, tailleCelluleDeg) {
    const cx = Math.floor(lng / tailleCelluleDeg);
    const cy = Math.floor(lat / tailleCelluleDeg);
    const point = L.latLng(lat, lng);
    for (let rayon = 1; rayon <= 6; rayon++) {
      let distMin = Infinity;
      let candidats = 0;
      for (let dx = -rayon; dx <= rayon; dx++) {
        for (let dy = -rayon; dy <= rayon; dy++) {
          const voisins = index.get((cx + dx) + ',' + (cy + dy));
          if (!voisins) continue;
          for (let k = 0; k < voisins.length; k++) {
            candidats++;
            const infra = infras[voisins[k]];
            const d = point.distanceTo(L.latLng(infra.latitude, infra.longitude));
            if (d < distMin) distMin = d;
          }
        }
      }
      if (candidats > 0) return distMin;
    }
    // Repli de securite (secteur tres peu dense autour de ce point) :
    // recherche exhaustive, pour garantir un resultat correct dans tous les cas.
    let distMin = Infinity;
    for (let i = 0; i < infras.length; i++) {
      const d = point.distanceTo(L.latLng(infras[i].latitude, infras[i].longitude));
      if (d < distMin) distMin = d;
    }
    return distMin;
  }

  // ===== Zones sous-desservies =====
  let coucheSousDesservis = null;

  function analyserZonesSousDesservies() {""",
))

# B) Boucle de la grille : construit l'index puis l'utilise.
PATCHES.append((
    "boucle grille",
    """      const pas = 0.0018; // environ 180 m a cette latitude
      const groupe = L.layerGroup();
      let cellulesSousDesservies = 0;
      let totalCellules = 0;
      const comptesParZone = {};

      for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += pas) {
        for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += pas) {
          if (!celluleDansLaCommune(lat, lng)) continue;
          totalCellules++;
          const point = L.latLng(lat, lng);
          let distMin = Infinity;
          for (let i = 0; i < infras.length; i++) {
            const d = point.distanceTo(L.latLng(infras[i].latitude, infras[i].longitude));
            if (d < distMin) distMin = d;
          }
""",
    """      const pas = 0.0018; // environ 180 m a cette latitude
      const groupe = L.layerGroup();
      let cellulesSousDesservies = 0;
      let totalCellules = 0;
      const comptesParZone = {};

      // Index spatial des infrastructures : chaque cellule/parcelle ne
      // compare plus qu'aux infrastructures proches, au lieu de toutes.
      const tailleCelluleIndex = Math.max(seuil, 50) / 111320;
      const indexInfra = construireIndexInfra(infras, tailleCelluleIndex);

      for (let lat = bounds.getSouth(); lat <= bounds.getNorth(); lat += pas) {
        for (let lng = bounds.getWest(); lng <= bounds.getEast(); lng += pas) {
          if (!celluleDansLaCommune(lat, lng)) continue;
          totalCellules++;
          const distMin = distanceMinIndexee(lat, lng, infras, indexInfra, tailleCelluleIndex);
""",
))

# C) Boucle des parcelles concernees : reutilise le meme index.
PATCHES.append((
    "boucle parcelles",
    """      const baseParcelles = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);
      let parcellesConcernees = 0;
      baseParcelles.forEach(function (f) {
        if (!f.geometry) return;
        let centre;
        try { centre = turf.centroid(f).geometry.coordinates; } catch (e) { return; }
        const point = L.latLng(centre[1], centre[0]);
        let distMin = Infinity;
        for (let i = 0; i < infras.length; i++) {
          const d = point.distanceTo(L.latLng(infras[i].latitude, infras[i].longitude));
          if (d < distMin) distMin = d;
        }
        if (distMin > seuil) parcellesConcernees++;
      });""",
    """      const baseParcelles = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);
      let parcellesConcernees = 0;
      baseParcelles.forEach(function (f) {
        if (!f.geometry) return;
        let centre;
        try { centre = turf.centroid(f).geometry.coordinates; } catch (e) { return; }
        const distMin = distanceMinIndexee(centre[1], centre[0], infras, indexInfra, tailleCelluleIndex);
        if (distMin > seuil) parcellesConcernees++;
      });""",
))

deja_tout_ok = "construireIndexInfra" in contenu

if deja_tout_ok:
    print("OK : deja applique, rien a faire.")
else:
    erreurs = []
    for nom, ancre, remplacement in PATCHES:
        if ancre not in contenu:
            erreurs.append(f"- ancre introuvable pour « {nom} »")
            continue
        if contenu.count(ancre) != 1:
            erreurs.append(f"- ancre « {nom} » trouvee {contenu.count(ancre)} fois (attendu 1)")
            continue
        contenu = contenu.replace(ancre, remplacement)

    if erreurs:
        print("ERREUR : certains blocs n'ont pas pu etre localises tels quels :")
        for e in erreurs:
            print(e)
        raise SystemExit("Aucun fichier n'a ete modifie (securite : tout ou rien).")

    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : analyse 'Zones sous-desservies' nettement accélérée (index spatial).")
    print("-> Rechargez simplement la page du geoportail public (pas besoin de redemarrer le serveur, c'est juste le template).")