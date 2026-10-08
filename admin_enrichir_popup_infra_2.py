CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_afficher = '''    (data.features || []).forEach(function (feature) {
      (feature.properties.infrastructures || []).forEach(function (infra) {
        if (infra.latitude == null || infra.longitude == null) return;
        if (!categoriesInfraActives.has(infra.categorie)) return;

        const icone = L.divIcon({
          className: '',
          html:
            '<div style="background:' + (infra.couleur || '#7b3fa0') + '; width:22px; height:22px; ' +
            'border-radius:50%; border:2px solid white; box-shadow:0 1px 4px rgba(0,0,0,0.4); ' +
            'display:flex; align-items:center; justify-content:center;">' +
              '<i class="fa-solid ' + (infra.icone || 'fa-map-pin') + '" style="color:white; font-size:10px;"></i>' +
            '</div>',
          iconSize: [22, 22],
          iconAnchor: [11, 11],
        });

        L.marker([infra.latitude, infra.longitude], { icon: icone })
          .bindPopup('<strong>' + infra.nom + '</strong><br><span style="color:#766c5d;">' + infra.categorie + '</span>')
          .addTo(coucheInfrastructuresAdmin);
      });
    });'''

nouveau_afficher = '''    toutesLesInfrastructures(data).forEach(function (infra) {
      if (infra.latitude == null || infra.longitude == null) return;
      if (!categoriesInfraActives.has(infra.categorie)) return;

      const icone = L.divIcon({
        className: '',
        html:
          '<div style="background:' + (infra.couleur || '#7b3fa0') + '; width:22px; height:22px; ' +
          'border-radius:50%; border:2px solid white; box-shadow:0 1px 4px rgba(0,0,0,0.4); ' +
          'display:flex; align-items:center; justify-content:center;">' +
            '<i class="fa-solid ' + (infra.icone || 'fa-map-pin') + '" style="color:white; font-size:10px;"></i>' +
          '</div>',
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });

      L.marker([infra.latitude, infra.longitude], { icon: icone })
        .bindPopup(construirePopupInfra(infra))
        .addTo(coucheInfrastructuresAdmin);
    });'''

if nouveau_afficher in contenu:
    print("DEJA FAIT : afficherIconesInfrastructures deja mise a jour.")
elif ancien_afficher in contenu:
    contenu = contenu.replace(ancien_afficher, nouveau_afficher, 1)
    changements += 1
    print("OK : afficherIconesInfrastructures affiche maintenant aussi les infra sans parcelle, avec popup enrichie.")
else:
    print("ERREUR : ancre afficherIconesInfrastructures introuvable.")

ancien_load = '''        allParcelles = data;
        redessinerCouches();
        populateInfraFilter();
        afficherIconesInfrastructures(data);'''

nouveau_load = '''        allParcelles = data;
        infraSansParcelle = data.infrastructures_hors_parcelle || [];
        redessinerCouches();
        populateInfraFilter();
        afficherIconesInfrastructures(data);'''

if nouveau_load in contenu:
    print("DEJA FAIT : loadParcelles deja mise a jour.")
elif ancien_load in contenu:
    contenu = contenu.replace(ancien_load, nouveau_load, 1)
    changements += 1
    print("OK : loadParcelles memorise maintenant infraSansParcelle.")
else:
    print("ERREUR : ancre loadParcelles introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 2/2). ===")