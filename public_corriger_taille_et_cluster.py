CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_init = '''    Promise.all([loadZones(), loadParcelles()]).finally(function () {
      const loader = document.getElementById('mapLoader');
      if (loader) loader.classList.add('hidden');
    });
  }'''

nouveau_init = '''    Promise.all([loadZones(), loadParcelles()]).finally(function () {
      const loader = document.getElementById('mapLoader');
      if (loader) loader.classList.add('hidden');
      map.invalidateSize();
    });

    if (window.ResizeObserver) {
      const conteneurCarte = document.getElementById('map');
      const resizeObserver = new ResizeObserver(function () {
        map.invalidateSize();
      });
      resizeObserver.observe(conteneurCarte);
    }

    window.addEventListener('resize', function () {
      if (map) map.invalidateSize();
    });
  }'''

if "ResizeObserver" in contenu.split("function loadZones")[0]:
    print("DEJA FAIT : recalcul de taille deja present.")
elif ancien_init in contenu:
    contenu = contenu.replace(ancien_init, nouveau_init, 1)
    changements += 1
    print("OK : recalcul automatique de la taille de la carte ajoute (ResizeObserver).")
else:
    print("ERREUR : ancre initMap introuvable.")

ancien_cluster = "coucheInfrastructures = L.markerClusterGroup({\n      iconCreateFunction: creerIconeCluster,\n      maxClusterRadius: 50,\n      spiderfyOnMaxZoom: true,\n    });"
nouveau_cluster = "coucheInfrastructures = L.layerGroup();"

if nouveau_cluster in contenu and "markerClusterGroup" not in contenu:
    print("DEJA FAIT : clustering deja retire.")
elif ancien_cluster in contenu:
    contenu = contenu.replace(ancien_cluster, nouveau_cluster, 1)
    changements += 1
    print("OK : clustering retire, retour aux icones individuelles.")
else:
    print("ERREUR : ancre clustering introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")