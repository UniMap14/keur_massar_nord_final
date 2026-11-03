# -*- coding: utf-8 -*-
"""
ADMIN - Feature 2/6 : afficher la zone/quartier touche quand on clique
"Me geolocaliser" (version admin : pas de "mes parcelles", car cela
depend d'un citoyen connecte, non pertinent pour le personnel admin).

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "function afficherZoneEtParcelle"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Nouvelle fonction, juste avant localiserMoi() ---
    ancien_fn = '''  }

  function localiserMoi() {'''
    if ancien_fn not in contenu:
        raise SystemExit("ANCRE avant localiserMoi() INTROUVABLE - abandon, rien n'a ete modifie.")

    nouveau_fn = '''  }

  function afficherZoneEtParcelle(lat, lng) {
    const status = document.getElementById('position-status');
    let messageSupplementaire = '';

    if (typeof turf !== 'undefined' && allZones && allZones.features && allZones.features.length) {
      const point = turf.point([lng, lat]);
      let zoneTrouvee = null;
      for (let i = 0; i < allZones.features.length; i++) {
        try {
          if (turf.booleanPointInPolygon(point, allZones.features[i])) {
            zoneTrouvee = allZones.features[i];
            break;
          }
        } catch (e) {}
      }
      if (zoneTrouvee) {
        const proprietes = zoneTrouvee.properties || {};
        const nomZone = proprietes.nom || proprietes.layer || 'zone inconnue';
        messageSupplementaire += '<div style="margin-top:4px;"><i class="fa-solid fa-draw-polygon"></i> Vous êtes dans : <strong>' + nomZone + '</strong></div>';
      } else {
        messageSupplementaire += '<div style="margin-top:4px; color:#766c5d;"><i class="fa-solid fa-draw-polygon"></i> Hors des zones cartographiées.</div>';
      }
    }

    if (messageSupplementaire) {
      status.innerHTML += messageSupplementaire;
    }
  }

  function localiserMoi() {'''
    contenu = contenu.replace(ancien_fn, nouveau_fn)

    # --- 2) Appel dans le callback de geolocalisation, apres afficherInfrastructuresProches(); ---
    ancien_appel = '''        status.innerHTML = '<span style="color:#2f7a4f;"><i class="fa-solid fa-check"></i> Position trouvée : ' + coordAffichees + '</span>';
        afficherInfrastructuresProches();'''
    if ancien_appel not in contenu:
        raise SystemExit("ANCRE appel afficherInfrastructuresProches INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_appel = '''        status.innerHTML = '<span style="color:#2f7a4f;"><i class="fa-solid fa-check"></i> Position trouvée : ' + coordAffichees + '</span>';
        afficherInfrastructuresProches();
        afficherZoneEtParcelle(pos.coords.latitude, pos.coords.longitude);'''
    contenu = contenu.replace(ancien_appel, nouveau_appel)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes (feature 2/6 : zone/quartier sur geolocalisation).")