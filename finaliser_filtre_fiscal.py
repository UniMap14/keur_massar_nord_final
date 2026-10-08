CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_redessine = '''  function redessinerCouches() {
    const parcellesAffichees = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);

    if (coucheParcelles) map.removeLayer(coucheParcelles);'''

nouveau_redessine = '''  function redessinerCouches() {
    let parcellesAffichees = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);
    if (peutFiscal && filtreFiscalActif) {
      parcellesAffichees = parcellesAffichees.filter(function (f) {
        return f.properties.statut_fiscal === filtreFiscalActif;
      });
    }

    if (coucheParcelles) map.removeLayer(coucheParcelles);'''

if "peutFiscal && filtreFiscalActif) {\n      parcellesAffichees = parcellesAffichees.filter" in contenu:
    print("DEJA FAIT : redessinerCouches deja modifie.")
elif ancien_redessine in contenu:
    contenu = contenu.replace(ancien_redessine, nouveau_redessine, 1)
    changements += 1
    print("OK : redessinerCouches applique maintenant le filtre fiscal.")
else:
    print("ERREUR : ancre redessinerCouches introuvable.")

ancien_fn = "  function initMap() {"

nouveau_fn = '''  function mettreAJourCompteursFiscaux() {
    if (!peutFiscal) return;
    const features = allParcelles.features || [];
    const compte = { '': features.length, A_JOUR: 0, EN_RETARD: 0, EXONERE: 0 };
    features.forEach(function (f) {
      const s = f.properties.statut_fiscal;
      if (compte.hasOwnProperty(s)) compte[s]++;
    });
    const maj = function (id, val) {
      const el = document.getElementById(id);
      if (el) el.textContent = val.toLocaleString('fr-FR');
    };
    maj('countToutes', compte['']);
    maj('countAjour', compte.A_JOUR);
    maj('countRetard', compte.EN_RETARD);
    maj('countExonere', compte.EXONERE);
  }

  function initFiltreFiscal() {
    if (!peutFiscal) return;
    const boutons = document.querySelectorAll('#filtreFiscalGroup .mc-filtre-btn');
    boutons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filtreFiscalActif = btn.getAttribute('data-statut');
        boutons.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        redessinerCouches();
      });
    });
  }

  function initMap() {'''

if "function mettreAJourCompteursFiscaux" in contenu:
    print("DEJA FAIT : fonctions deja presentes.")
elif ancien_fn in contenu:
    contenu = contenu.replace(ancien_fn, nouveau_fn, 1)
    changements += 1
    print("OK : fonctions mettreAJourCompteursFiscaux / initFiltreFiscal ajoutees.")
else:
    print("ERREUR : ancre initMap introuvable.")

ancien_appel = '''    try {
      initMap();
    } catch (e) {'''

nouveau_appel = '''    try {
      initMap();
      initFiltreFiscal();
    } catch (e) {'''

if "initFiltreFiscal();\n    } catch" in contenu:
    print("DEJA FAIT : appel deja present.")
elif ancien_appel in contenu:
    contenu = contenu.replace(ancien_appel, nouveau_appel, 1)
    changements += 1
    print("OK : initFiltreFiscal() appelee au demarrage.")
else:
    print("ERREUR : ancre appel introuvable.")

ancien_load = '''      .then(function (data) {
        allParcelles = data;
        redessinerCouches();
        populateZoneFilter();
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {
          map.fitBounds(coucheParcelles.getBounds(), { padding: [20, 20] });
        }
      })
      .catch(function (e) { console.error('Erreur parcelles admin:', e); });'''

nouveau_load = '''      .then(function (data) {
        allParcelles = data;
        redessinerCouches();
        populateZoneFilter();
        mettreAJourCompteursFiscaux();
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {
          map.fitBounds(coucheParcelles.getBounds(), { padding: [20, 20] });
        }
      })
      .catch(function (e) { console.error('Erreur parcelles admin:', e); });'''

if "mettreAJourCompteursFiscaux();\n        if (coucheParcelles" in contenu:
    print("DEJA FAIT : loadParcelles deja modifie.")
elif ancien_load in contenu:
    contenu = contenu.replace(ancien_load, nouveau_load, 1)
    changements += 1
    print("OK : loadParcelles met a jour les compteurs apres chargement.")
else:
    print("ERREUR : ancre loadParcelles introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")