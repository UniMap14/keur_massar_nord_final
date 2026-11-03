# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_voronoi_admin.py', encoding='utf-8').read())"
"""
chemin = "foncier/templates/foncier/geoportail_admin.html"
with open(chemin, "r", encoding="utf-8", errors="replace") as f:
    contenu = f.read()

print("LONGUEUR TOTALE geoportail_admin.html :", len(contenu), "caracteres")
print()

ANCRE_A = """  // ===== Zones sous-desservies =====
  let coucheSousDesservis = null;

  function analyserZonesSousDesservies() {"""

ANCRE_B = """      const pas = 0.0018; // environ 180 m a cette latitude
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
"""

ANCRE_C = """      const baseParcelles = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);
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
      });"""

for nom, ancre in [("A (helpers)", ANCRE_A), ("B (boucle grille)", ANCRE_B), ("C (boucle parcelles)", ANCRE_C)]:
    print(f"Ancre {nom} presente exactement telle quelle :", contenu.count(ancre), "fois")

print()
print("'construireIndexInfra' deja present :", "construireIndexInfra" in contenu)