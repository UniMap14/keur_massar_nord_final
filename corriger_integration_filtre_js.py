CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_redessine = '''  function redessinerCouches() {
    let parcellesAffichees = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);
    if (peutFiscal && filtreFiscalActif) {
      parcellesAffichees = parcellesAffichees.filter(function (f) {
        return f.properties.statut_fiscal === filtreFiscalActif;
      });
    }

    if (coucheParcelles) map.removeLayer(coucheParcelles);'''

nouveau_redessine = '''  function redessinerCouches() {
    const parcellesAffichees = filteredParcelles.length > 0 ? filteredParcelles : (allParcelles.features || []);

    if (coucheParcelles) map.removeLayer(coucheParcelles);'''

if nouveau_redessine in contenu:
    print("DEJA FAIT : redessinerCouches deja corrige.")
elif ancien_redessine in contenu:
    contenu = contenu.replace(ancien_redessine, nouveau_redessine, 1)
    changements += 1
    print("OK : double-filtrage retire de redessinerCouches.")
else:
    print("ERREUR : ancre redessinerCouches introuvable.")

ancien_fn = '''  function mettreAJourCompteursFiscaux() {
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

nouveau_fn = "  function initMap() {"

if ancien_fn in contenu:
    contenu = contenu.replace(ancien_fn, nouveau_fn, 1)
    changements += 1
    print("OK : fonctions mettreAJourCompteursFiscaux / initFiltreFiscal retirees.")
elif "function mettreAJourCompteursFiscaux" not in contenu:
    print("DEJA FAIT : fonctions deja retirees.")
else:
    print("ERREUR : ancre fonctions introuvable.")

ancien_appel = '''    try {
      initMap();
      initFiltreFiscal();
    } catch (e) {'''

nouveau_appel = '''    try {
      initMap();
    } catch (e) {'''

if nouveau_appel in contenu and "initFiltreFiscal();" not in contenu:
    print("DEJA FAIT : appel deja retire.")
elif ancien_appel in contenu:
    contenu = contenu.replace(ancien_appel, nouveau_appel, 1)
    changements += 1
    print("OK : appel a initFiltreFiscal() retire.")
else:
    print("ERREUR : ancre appel introuvable.")

ancien_load = '''        redessinerCouches();
        populateZoneFilter();
        mettreAJourCompteursFiscaux();
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {'''

nouveau_load = '''        redessinerCouches();
        populateZoneFilter();
        if (coucheParcelles && coucheParcelles.getBounds().isValid()) {'''

if nouveau_load in contenu and "mettreAJourCompteursFiscaux();" not in contenu:
    print("DEJA FAIT : loadParcelles deja corrige.")
elif ancien_load in contenu:
    contenu = contenu.replace(ancien_load, nouveau_load, 1)
    changements += 1
    print("OK : appel a mettreAJourCompteursFiscaux retire de loadParcelles.")
else:
    print("ERREUR : ancre loadParcelles introuvable.")

ancien_apply = '''  function applyFilters() {
    const zoneFilter = document.getElementById('filter-zone').value;
    const statutFilter = document.getElementById('filter-statut').value;

    let filtered = allParcelles.features || [];
    if (zoneFilter) {
      filtered = filtered.filter(function (f) { return zoneLabelDe(f) === zoneFilter; });
    }
    if (statutFilter) {
      filtered = filtered.filter(function (f) { return f.properties.statut_fiscal === statutFilter; });
    }

    filteredParcelles = filtered;'''

nouveau_apply = '''  function applyFilters() {
    const zoneFilter = document.getElementById('filter-zone').value;
    const statutSelect = document.getElementById('filter-statut');
    const statutFilter = statutSelect ? statutSelect.value : '';

    filtreFiscalActif = statutFilter;

    let filtered = allParcelles.features || [];
    if (zoneFilter) {
      filtered = filtered.filter(function (f) { return zoneLabelDe(f) === zoneFilter; });
    }
    if (statutFilter && statutFilter !== 'TOUS_COLORES') {
      filtered = filtered.filter(function (f) { return f.properties.statut_fiscal === statutFilter; });
    }

    filteredParcelles = filtered;'''

if "statutFilter !== 'TOUS_COLORES'" in contenu:
    print("DEJA FAIT : applyFilters deja corrige.")
elif ancien_apply in contenu:
    contenu = contenu.replace(ancien_apply, nouveau_apply, 1)
    changements += 1
    print("OK : applyFilters gere maintenant l'option 'Toutes avec couleurs'.")
else:
    print("ERREUR : ancre applyFilters introuvable.")

ancien_reinit = '''  function reinitialiserFiltres() {
    document.getElementById('filter-zone').value = '';
    document.getElementById('filter-statut').value = '';
    document.getElementById('search-nicad').value = '';
    document.getElementById('search-result').textContent = '';
    filteredParcelles = [];
    redessinerCouches();
  }'''

nouveau_reinit = '''  function reinitialiserFiltres() {
    document.getElementById('filter-zone').value = '';
    const statutSelect = document.getElementById('filter-statut');
    if (statutSelect) statutSelect.value = '';
    document.getElementById('search-nicad').value = '';
    document.getElementById('search-result').textContent = '';
    filteredParcelles = [];
    filtreFiscalActif = '';
    redessinerCouches();
  }'''

if "if (statutSelect) statutSelect.value" in contenu:
    print("DEJA FAIT : reinitialiserFiltres deja corrige.")
elif ancien_reinit in contenu:
    contenu = contenu.replace(ancien_reinit, nouveau_reinit, 1)
    changements += 1
    print("OK : reinitialiserFiltres remet aussi filtreFiscalActif a vide.")
else:
    print("ERREUR : ancre reinitialiserFiltres introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 2/2). ===")