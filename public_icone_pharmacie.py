CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_fn = "  function construirePopupInfra(infra) {"

nouveau_fn = '''  function apparenceInfra(infra) {
    if (infra.sous_type === 'Pharmacie') {
      return { couleur: '#2f7a4f', icone: 'fa-plus' };
    }
    return { couleur: infra.couleur || '#7b3fa0', icone: infra.icone || 'fa-map-pin' };
  }

  function construirePopupInfra(infra) {'''

if "function apparenceInfra" in contenu:
    print("DEJA FAIT : fonction apparenceInfra deja presente.")
elif ancien_fn in contenu:
    contenu = contenu.replace(ancien_fn, nouveau_fn, 1)
    changements += 1
    print("OK : fonction apparenceInfra ajoutee.")
else:
    print("ERREUR : ancre introuvable.")

ancien_marqueur = '''      const icone = L.divIcon({
        className: '',
        html:
          '<div style="background:' + (infra.couleur || '#7b3fa0') + '; width:24px; height:24px; ' +
          'border-radius:50%; border:2px solid white; box-shadow:0 1px 4px rgba(0,0,0,0.4); ' +
          'display:flex; align-items:center; justify-content:center;">' +
            '<i class="fa-solid ' + (infra.icone || 'fa-map-pin') + '" style="color:white; font-size:11px;"></i>' +
          '</div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });'''

nouveau_marqueur = '''      const apparence = apparenceInfra(infra);
      const icone = L.divIcon({
        className: '',
        html:
          '<div style="background:' + apparence.couleur + '; width:24px; height:24px; ' +
          'border-radius:50%; border:2px solid white; box-shadow:0 1px 4px rgba(0,0,0,0.4); ' +
          'display:flex; align-items:center; justify-content:center;">' +
            '<i class="fa-solid ' + apparence.icone + '" style="color:white; font-size:11px;"></i>' +
          '</div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });'''

if nouveau_marqueur in contenu:
    print("DEJA FAIT : creation du marqueur deja mise a jour.")
elif ancien_marqueur in contenu:
    contenu = contenu.replace(ancien_marqueur, nouveau_marqueur, 1)
    changements += 1
    print("OK : marqueurs utilisent maintenant apparenceInfra() (pharmacie = croix verte).")
else:
    print("ERREUR : ancre marqueur introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")