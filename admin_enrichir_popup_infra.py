CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_fn = '''  let coucheInfrastructuresAdmin = null;
  let categoriesInfraVues = {};
  let categoriesInfraActives = new Set();

  function collecterCategoriesInfra() {
    categoriesInfraVues = {};
    (allParcelles.features || []).forEach(function (f) {
      (f.properties.infrastructures || []).forEach(function (infra) {
        if (!categoriesInfraVues[infra.categorie]) {
          categoriesInfraVues[infra.categorie] = { couleur: infra.couleur, icone: infra.icone };
        }
      });
    });
  }'''

nouveau_fn = '''  let coucheInfrastructuresAdmin = null;
  let categoriesInfraVues = {};
  let categoriesInfraActives = new Set();
  let infraSansParcelle = [];

  function construirePopupInfra(infra) {
    let html = '<div style="min-width:190px;">';
    html += '<strong>' + infra.nom + '</strong>';
    html += '<br><span style="color:#766c5d; font-size:12px;">' + (infra.sous_type || infra.categorie) + '</span>';
    const details = infra.details || {};
    const cles = Object.keys(details);
    if (cles.length > 0) {
      html += '<table style="font-size:12px; width:100%; margin-top:6px; border-top:1px solid #eee; padding-top:6px;">';
      cles.forEach(function (cle) {
        html += '<tr><td style="color:#766c5d; padding-right:10px; vertical-align:top;">' + cle + '</td><td style="font-weight:600;">' + details[cle] + '</td></tr>';
      });
      html += '</table>';
    }
    html += '</div>';
    return html;
  }

  function toutesLesInfrastructures(data) {
    const liste = [];
    (data.features || []).forEach(function (f) {
      (f.properties.infrastructures || []).forEach(function (infra) { liste.push(infra); });
    });
    (data.infrastructures_hors_parcelle || []).forEach(function (infra) { liste.push(infra); });
    return liste;
  }

  function collecterCategoriesInfra() {
    categoriesInfraVues = {};
    toutesLesInfrastructures({ features: allParcelles.features, infrastructures_hors_parcelle: infraSansParcelle }).forEach(function (infra) {
      if (!categoriesInfraVues[infra.categorie]) {
        categoriesInfraVues[infra.categorie] = { couleur: infra.couleur, icone: infra.icone };
      }
    });
  }'''

if "function construirePopupInfra" in contenu:
    print("DEJA FAIT : fonctions deja presentes.")
elif ancien_fn in contenu:
    contenu = contenu.replace(ancien_fn, nouveau_fn, 1)
    changements += 1
    print("OK : construirePopupInfra / toutesLesInfrastructures ajoutees, collecterCategoriesInfra mise a jour.")
else:
    print("ERREUR : ancre fonctions introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 1/2). ===")