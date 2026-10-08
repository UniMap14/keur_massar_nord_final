CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- 1. Retire le clustering : infrastructures toujours affichees individuellement,
#        cliquables directement, comme sur le geoportail public ---
ancien_cluster = '''  let clusteringActif = true;
  let coucheChaleur = null;
  let modeChaleurActif = false;
  let dernieresDonneesInfra = null;'''

nouveau_cluster = '''  let coucheChaleur = null;
  let modeChaleurActif = false;
  let dernieresDonneesInfra = null;'''

if "let clusteringActif" not in contenu:
    resultats.append("IGNORE : clustering deja retire.")
elif ancien_cluster in contenu:
    contenu = contenu.replace(ancien_cluster, nouveau_cluster, 1)
    resultats.append("OK : variable clusteringActif retiree.")
else:
    resultats.append("ERREUR : bloc clusteringActif introuvable.")

ancien_groupe = '''    coucheInfrastructuresAdmin = clusteringActif
      ? L.markerClusterGroup({
          iconCreateFunction: creerIconeCluster,
          maxClusterRadius: 50,
          spiderfyOnMaxZoom: true,
        })
      : L.layerGroup();'''

nouveau_groupe = '''    coucheInfrastructuresAdmin = L.layerGroup();'''

if "coucheInfrastructuresAdmin = L.layerGroup();" in contenu and ancien_groupe not in contenu:
    resultats.append("IGNORE : couche infrastructures deja simplifiee.")
elif ancien_groupe in contenu:
    contenu = contenu.replace(ancien_groupe, nouveau_groupe, 1)
    resultats.append("OK : infrastructures affichees individuellement (sans regroupement).")
else:
    resultats.append("ERREUR : bloc creation du groupe introuvable.")

# --- 2. Securise l'affichage des montants FCFA (evite "NaN FCFA") ---
ancien_montant = '''function libelleStatut(statut) {
    if (statut === 'EN_RETARD') return 'En retard';
    if (statut === 'EXONERE') return 'Exonéré';
    return 'À jour';
  }'''

nouveau_montant = '''function libelleStatut(statut) {
    if (statut === 'EN_RETARD') return 'En retard';
    if (statut === 'EXONERE') return 'Exonéré';
    return 'À jour';
  }

  function fcfaOuTiret(valeur) {
    const nombre = Number(valeur);
    if (valeur === null || valeur === undefined || valeur === '' || isNaN(nombre)) return '—';
    return nombre.toLocaleString('fr-FR') + ' FCFA';
  }'''

if "function fcfaOuTiret" in contenu:
    resultats.append("IGNORE : fonction fcfaOuTiret deja presente.")
elif ancien_montant in contenu:
    contenu = contenu.replace(ancien_montant, nouveau_montant, 1)
    resultats.append("OK : fonction fcfaOuTiret ajoutee (evite les NaN FCFA).")
else:
    resultats.append("ERREUR : point d'insertion fcfaOuTiret introuvable.")

# --- 3. Utilise fcfaOuTiret dans la fiche parcelle au lieu du formatage direct ---
ancien_fiche = '''        <span class="ep-view-value">${Number(p.montant_taxe_annuelle).toLocaleString('fr-FR')} FCFA${p.simulation_fiscale ? ' <span class="ep-badge-simu" title="Montant simulé à des fins académiques, non une donnée fiscale réelle">🔬 Simulation</span>' : ''}</span>
      </div>
      <div class="ep-view-row">
        <span class="ep-view-label">Valeur locative</span>
        <span class="ep-view-value">${Number(p.valeur_locative).toLocaleString('fr-FR')} FCFA</span>'''

nouveau_fiche = '''        <span class="ep-view-value">${fcfaOuTiret(p.montant_taxe_annuelle)}${p.simulation_fiscale ? ' <span class="ep-badge-simu" title="Montant simulé à des fins académiques, non une donnée fiscale réelle">🔬 Simulation</span>' : ''}</span>
      </div>
      <div class="ep-view-row">
        <span class="ep-view-label">Valeur locative</span>
        <span class="ep-view-value">${fcfaOuTiret(p.valeur_locative)}</span>'''

if "fcfaOuTiret(p.montant_taxe_annuelle)" in contenu:
    resultats.append("IGNORE : fiche parcelle deja securisee.")
elif ancien_fiche in contenu:
    contenu = contenu.replace(ancien_fiche, nouveau_fiche, 1)
    resultats.append("OK : fiche parcelle utilise l'affichage securise des montants.")
else:
    resultats.append("ERREUR : bloc de la fiche parcelle introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))