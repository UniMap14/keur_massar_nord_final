CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''              (props.adresse_parcelle ? '<div class="fp-row"><span class="fp-label">Secteur</span><span class="fp-value">' + props.adresse_parcelle + '</span></div>' : '') +
              '<a class="fp-link" href="{% url "recherche_cadastrale" %}?q=' + encodeURIComponent(props.nicad || '') + '">Voir la fiche complète →</a>' +
            '</div>';'''

nouveau = '''              (props.adresse_parcelle ? '<div class="fp-row"><span class="fp-label">Secteur</span><span class="fp-value">' + props.adresse_parcelle + '</span></div>' : '') +
              ((props.infrastructures && props.infrastructures.length > 0) ?
                '<div class="fp-row" style="flex-direction:column; align-items:flex-start; gap:4px;">' +
                  '<span class="fp-label" style="color:#7b3fa0;"><i class="fa-solid fa-building"></i> Infrastructure(s) sur cette parcelle</span>' +
                  props.infrastructures.map(function (i) {
                    return '<span class="fp-value" style="font-size:12.5px;">' + i.nom + ' <em style="color:#766c5d;">(' + i.categorie + ')</em></span>';
                  }).join('') +
                '</div>'
              : '') +
              '<a class="fp-link" href="{% url "recherche_cadastrale" %}?q=' + encodeURIComponent(props.nicad || '') + '">Voir la fiche complète →</a>' +
            '</div>';'''

if "fp-label\" style=\"color:#7b3fa0;" in contenu:
    print("DEJA FAIT : deja modifie.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : section infrastructure ajoutee au popup.")
else:
    print("ERREUR : bloc exact introuvable.")