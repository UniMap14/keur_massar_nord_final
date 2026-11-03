# -*- coding: utf-8 -*-
"""
Ajoute une petite carte Leaflet (clic pour placer un repere) au-dessus des
champs Latitude / Longitude dans le formulaire de creation/modification
d'une Infrastructure, tout en gardant la saisie manuelle des coordonnees.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_carte_infrastructure.py
"""
import os

CHEMIN = os.path.join("foncier", "templates", "dashboard", "infrastructure_form.html")

if not os.path.exists(CHEMIN):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN}")

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

# ------------------------------------------------------------------
# 1) Charger Leaflet (CSS/JS) dans extra_head, a cote du <style> existant
# ------------------------------------------------------------------
ANCRE_HEAD = (
    '    .form-actions .btn { display: inline-flex; align-items: center; gap: 8px; }\n'
    '</style>\n'
    '{% endblock %}'
)
REMPLACEMENT_HEAD = (
    '    .form-actions .btn { display: inline-flex; align-items: center; gap: 8px; }\n'
    '</style>\n'
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">\n'
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n'
    '{% endblock %}'
)

deja_ok_head = REMPLACEMENT_HEAD in contenu

if not deja_ok_head:
    if ANCRE_HEAD not in contenu:
        raise SystemExit(
            "ERREUR : ancre HEAD introuvable dans infrastructure_form.html.\n"
            "Le fichier a peut-etre deja ete modifie. Aucun changement effectue."
        )
    if contenu.count(ANCRE_HEAD) != 1:
        raise SystemExit("ERREUR : ancre HEAD trouvee plusieurs fois, patch annule par securite.")
    contenu = contenu.replace(ANCRE_HEAD, REMPLACEMENT_HEAD)

# ------------------------------------------------------------------
# 2) Ajouter la carte + le script de synchronisation au-dessus des
#    champs Latitude / Longitude (les deux champs restent inchanges,
#    toujours modifiables a la main).
# ------------------------------------------------------------------
ANCRE_CHAMPS = (
    '        <div class="form-field">\n'
    '          <label for="{{ form.latitude.id_for_label }}"><i class="fa-solid fa-location-dot"></i> Latitude</label>\n'
    '          {{ form.latitude }}\n'
    '          {{ form.latitude.errors }}\n'
    '          <div class="hint">Facultatif — utile pour un futur affichage sur le géoportail.</div>\n'
    '        </div>\n'
    '\n'
    '        <div class="form-field">\n'
    '          <label for="{{ form.longitude.id_for_label }}"><i class="fa-solid fa-location-dot"></i> Longitude</label>\n'
    '          {{ form.longitude }}\n'
    '          {{ form.longitude.errors }}\n'
    '        </div>'
)

REMPLACEMENT_CHAMPS = (
    '        <div class="form-field full">\n'
    '          <label><i class="fa-solid fa-map-location-dot"></i> Localisation sur la carte</label>\n'
    '          <div class="leaflet-map-wrap" style="position:relative;">\n'
    '            <div id="infra-position-map" style="height:320px; border-radius:8px;"></div>\n'
    '          </div>\n'
    '          <div class="hint">\n'
    '            <i class="fa-solid fa-circle-info"></i>\n'
    '            Cliquez sur la carte pour placer ou déplacer le repère — les champs Latitude / Longitude ci-dessous\n'
    '            se remplissent automatiquement. Vous pouvez aussi saisir les coordonnées directement à la main.\n'
    '          </div>\n'
    '        </div>\n'
    '\n'
    '        <div class="form-field">\n'
    '          <label for="{{ form.latitude.id_for_label }}"><i class="fa-solid fa-location-dot"></i> Latitude</label>\n'
    '          {{ form.latitude }}\n'
    '          {{ form.latitude.errors }}\n'
    '          <div class="hint">Facultatif — utile pour un futur affichage sur le géoportail.</div>\n'
    '        </div>\n'
    '\n'
    '        <div class="form-field">\n'
    '          <label for="{{ form.longitude.id_for_label }}"><i class="fa-solid fa-location-dot"></i> Longitude</label>\n'
    '          {{ form.longitude }}\n'
    '          {{ form.longitude.errors }}\n'
    '        </div>\n'
    '\n'
    '        <script>\n'
    '        (function () {\n'
    '          function initInfraPositionMap() {\n'
    '            var mapEl = document.getElementById("infra-position-map");\n'
    '            var latInput = document.getElementById("{{ form.latitude.id_for_label }}");\n'
    '            var lonInput = document.getElementById("{{ form.longitude.id_for_label }}");\n'
    '            if (!mapEl || !latInput || !lonInput || mapEl._leafletInitDone) {\n'
    '              return;\n'
    '            }\n'
    '            mapEl._leafletInitDone = true;\n'
    '\n'
    '            var defautLat = 14.7900;\n'
    '            var defautLon = -17.3100;\n'
    '            var defautZoom = 14;\n'
    '\n'
    '            var latDepart = parseFloat(latInput.value);\n'
    '            var lonDepart = parseFloat(lonInput.value);\n'
    '            var aUnePosition = !isNaN(latDepart) && !isNaN(lonDepart);\n'
    '\n'
    '            var map = L.map("infra-position-map").setView(\n'
    '              aUnePosition ? [latDepart, lonDepart] : [defautLat, defautLon],\n'
    '              aUnePosition ? 16 : defautZoom\n'
    '            );\n'
    '\n'
    '            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {\n'
    '              attribution: \'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors\',\n'
    '              maxZoom: 19,\n'
    '              subdomains: "abc"\n'
    '            }).addTo(map);\n'
    '\n'
    '            var marker = null;\n'
    '\n'
    '            function placerRepere(lat, lon) {\n'
    '              if (marker) {\n'
    '                marker.setLatLng([lat, lon]);\n'
    '              } else {\n'
    '                marker = L.marker([lat, lon], { draggable: true }).addTo(map);\n'
    '                marker.on("dragend", function () {\n'
    '                  var pos = marker.getLatLng();\n'
    '                  latInput.value = pos.lat.toFixed(6);\n'
    '                  lonInput.value = pos.lng.toFixed(6);\n'
    '                });\n'
    '              }\n'
    '            }\n'
    '\n'
    '            if (aUnePosition) {\n'
    '              placerRepere(latDepart, lonDepart);\n'
    '            }\n'
    '\n'
    '            map.on("click", function (e) {\n'
    '              placerRepere(e.latlng.lat, e.latlng.lng);\n'
    '              latInput.value = e.latlng.lat.toFixed(6);\n'
    '              lonInput.value = e.latlng.lng.toFixed(6);\n'
    '            });\n'
    '\n'
    '            function syncDepuisChamps() {\n'
    '              var lat = parseFloat(latInput.value);\n'
    '              var lon = parseFloat(lonInput.value);\n'
    '              if (!isNaN(lat) && !isNaN(lon)) {\n'
    '                placerRepere(lat, lon);\n'
    '                map.panTo([lat, lon]);\n'
    '              }\n'
    '            }\n'
    '            latInput.addEventListener("change", syncDepuisChamps);\n'
    '            lonInput.addEventListener("change", syncDepuisChamps);\n'
    '\n'
    '            setTimeout(function () { map.invalidateSize(); }, 200);\n'
    '          }\n'
    '\n'
    '          if (typeof L === "undefined") {\n'
    '            var tentatives = 0;\n'
    '            var attendreLeaflet = setInterval(function () {\n'
    '              tentatives += 1;\n'
    '              if (typeof L !== "undefined") {\n'
    '                clearInterval(attendreLeaflet);\n'
    '                initInfraPositionMap();\n'
    '              } else if (tentatives > 100) {\n'
    '                clearInterval(attendreLeaflet);\n'
    '                console.error("Leaflet n\'a pas pu etre charge.");\n'
    '              }\n'
    '            }, 100);\n'
    '          } else {\n'
    '            initInfraPositionMap();\n'
    '          }\n'
    '        })();\n'
    '        </script>'
)

deja_ok_champs = '"infra-position-map"' in contenu

if not deja_ok_champs:
    if ANCRE_CHAMPS not in contenu:
        raise SystemExit(
            "ERREUR : ancre CHAMPS (Latitude/Longitude) introuvable dans infrastructure_form.html.\n"
            "Le fichier a peut-etre deja ete modifie. Aucun changement effectue."
        )
    if contenu.count(ANCRE_CHAMPS) != 1:
        raise SystemExit("ERREUR : ancre CHAMPS trouvee plusieurs fois, patch annule par securite.")
    contenu = contenu.replace(ANCRE_CHAMPS, REMPLACEMENT_CHAMPS)

if deja_ok_head and deja_ok_champs:
    print("OK : deja applique, rien a faire.")
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : carte de positionnement ajoutee dans {CHEMIN}")
    print("-> Rechargez simplement la page (pas besoin de redemarrer le serveur, c'est juste un template).")