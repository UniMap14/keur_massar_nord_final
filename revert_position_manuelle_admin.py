# -*- coding: utf-8 -*-
import io

CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    lignes = f.readlines()


def trouver(sous_chaine, depart=0):
    for i in range(depart, len(lignes)):
        if sous_chaine in lignes[i]:
            return i
    raise ValueError("Introuvable : " + sous_chaine)


idx_onevent = trouver("onEvent('btnPositionManuelle'")
del lignes[idx_onevent]
print("OK 1/4 : cablage du bouton retire")


idx_start = trouver("let modePositionManuelle = false;")
idx_calc = trouver("function calculerItineraire", idx_start)
idx_end = idx_calc - 1

original_localiserMoi = """  function localiserMoi() {
    const status = document.getElementById('position-status');
    if (!navigator.geolocation) { status.innerHTML = '<span style="color:#b23b2e;">Géolocalisation non supportée.</span>'; return; }
    status.textContent = 'Localisation en cours...';
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        userLatLng = [pos.coords.latitude, pos.coords.longitude];
        if (userMarker) map.removeLayer(userMarker);
        const icone = L.divIcon({ className: '', html: '<div style="background:#c9982e; width:16px; height:16px; border-radius:50%; border:3px solid white; box-shadow:0 0 6px rgba(0,0,0,0.5);"></div>', iconSize: [16, 16] });
        userMarker = L.marker(userLatLng, { icon: icone }).addTo(map).bindPopup('Vous êtes ici');
        map.flyTo(userLatLng, 15);
        status.innerHTML = '<span style="color:#2f7a4f;"><i class="fa-solid fa-check"></i> Position trouvée.</span>';
        afficherInfrastructuresProches();
      },
      function (err) { status.innerHTML = '<span style="color:#b23b2e;">Impossible de récupérer votre position (' + err.message + ').</span>'; },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }
"""

lignes[idx_start:idx_end + 1] = [original_localiserMoi]
print("OK 2/4 : localiserMoi() restauree (mode manuel retire)")


idx_mapinit = trouver("map = L.map(")
idx_click = idx_mapinit + 1
if "map.on('click'" in lignes[idx_click]:
    del lignes[idx_click:idx_click + 3]
    print("OK 3/4 : ecoute du clic sur la carte retiree")
else:
    print("ATTENTION 3/4 : bloc map.on('click', ...) introuvable a l'emplacement attendu, verifie manuellement")


idx_btn = trouver('id="btnPositionManuelle"')
idx_fin_btn = trouver("</button>", idx_btn)
del lignes[idx_btn:idx_fin_btn + 1]
print("OK 4/4 : bouton HTML retire")


with io.open(CHEMIN, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lignes)

print("")
print("Fichier sauvegarde : " + CHEMIN)
