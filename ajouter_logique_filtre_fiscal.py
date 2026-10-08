CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_var = "  const csrftoken = getCookie('csrftoken');"
nouveau_var = '''  const csrftoken = getCookie('csrftoken');
  const peutFiscal = {% if peut_fiscal %}true{% else %}false{% endif %};
  let filtreFiscalActif = '';'''

if "let filtreFiscalActif" in contenu:
    print("DEJA FAIT : variables deja presentes.")
elif ancien_var in contenu:
    contenu = contenu.replace(ancien_var, nouveau_var, 1)
    changements += 1
    print("OK : variables peutFiscal / filtreFiscalActif ajoutees.")
else:
    print("ERREUR : ancre variables introuvable.")

ancien_style = '''  function styleParcelle(feature) {
    const estSelectionnee = idDeFeature(feature) === idDeFeature(selectedFeature);
    return {
      renderer: renduCanvas,
      color: estSelectionnee ? '#f59e0b' : '#ffffff',
      weight: estSelectionnee ? 2 : 1,
      fillColor: estSelectionnee ? '#f59e0b' : couleurStatut(feature.properties.statut_fiscal),
      fillOpacity: estSelectionnee ? 0.75 : 0.55,
    };
  }'''

nouveau_style = '''  function styleParcelle(feature) {
    const estSelectionnee = idDeFeature(feature) === idDeFeature(selectedFeature);
    const afficherStatut = peutFiscal && filtreFiscalActif;
    const couleurBase = afficherStatut ? couleurStatut(feature.properties.statut_fiscal) : '#c9982e';
    return {
      renderer: renduCanvas,
      color: estSelectionnee ? '#f59e0b' : '#ffffff',
      weight: estSelectionnee ? 2 : 1,
      fillColor: estSelectionnee ? '#f59e0b' : couleurBase,
      fillOpacity: estSelectionnee ? 0.75 : 0.55,
    };
  }'''

if "afficherStatut" in contenu:
    print("DEJA FAIT : styleParcelle deja modifie.")
elif ancien_style in contenu:
    contenu = contenu.replace(ancien_style, nouveau_style, 1)
    changements += 1
    print("OK : styleParcelle neutre par defaut, colore seulement si filtre actif.")
else:
    print("ERREUR : ancre styleParcelle introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")