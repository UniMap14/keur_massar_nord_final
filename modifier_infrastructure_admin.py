CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- 1. Ajoute la constante URL_INFRA_UPDATE_TEMPLATE a cote de celle des parcelles ---
ancien_url = """  const URL_UPDATE_TEMPLATE = '{% url "parcelle_update_fiscal" 0 %}';"""
nouveau_url = """  const URL_UPDATE_TEMPLATE = '{% url "parcelle_update_fiscal" 0 %}';
  const URL_INFRA_UPDATE_TEMPLATE = '{% url "dashboard_infrastructure_update" 0 %}';"""

if "URL_INFRA_UPDATE_TEMPLATE" in contenu:
    resultats.append("IGNORE : constante URL infra deja presente.")
elif ancien_url in contenu:
    contenu = contenu.replace(ancien_url, nouveau_url, 1)
    resultats.append("OK : constante URL_INFRA_UPDATE_TEMPLATE ajoutee.")
else:
    resultats.append("ERREUR : ligne URL_UPDATE_TEMPLATE introuvable.")

# --- 2. Ajoute le lien "Modifier" dans la popup d'infrastructure ---
ancien_popup = '''  function construirePopupInfra(infra) {
    let html = '<div style="min-width:190px;"><strong>' + infra.nom + '</strong>';
    html += '<br><span style="color:#766c5d; font-size:12px;">' + (infra.sous_type || infra.categorie) + '</span>';
    const details = infra.details || {};
    const cles = Object.keys(details);
    if (cles.length > 0) {
      html += '<table style="font-size:12px; width:100%; margin-top:6px; border-top:1px solid #eee; padding-top:6px;">';
      cles.forEach(function (cle) { html += '<tr><td style="color:#766c5d; padding-right:10px; vertical-align:top;">' + cle + '</td><td style="font-weight:600;">' + details[cle] + '</td></tr>'; });
      html += '</table>';
    }
    html += '</div>';
    return html;
  }'''

nouveau_popup = '''  function construirePopupInfra(infra) {
    let html = '<div style="min-width:190px;"><strong>' + infra.nom + '</strong>';
    html += '<br><span style="color:#766c5d; font-size:12px;">' + (infra.sous_type || infra.categorie) + '</span>';
    const details = infra.details || {};
    const cles = Object.keys(details);
    if (cles.length > 0) {
      html += '<table style="font-size:12px; width:100%; margin-top:6px; border-top:1px solid #eee; padding-top:6px;">';
      cles.forEach(function (cle) { html += '<tr><td style="color:#766c5d; padding-right:10px; vertical-align:top;">' + cle + '</td><td style="font-weight:600;">' + details[cle] + '</td></tr>'; });
      html += '</table>';
    }
    if (peutTechnique && infra.id) {
      html += '<a href="' + URL_INFRA_UPDATE_TEMPLATE.replace('0', infra.id) + '" target="_blank" rel="noopener" style="display:inline-block; margin-top:8px; font-size:12px; font-weight:700; color:#2f7a4f; text-decoration:none;"><i class="fa-solid fa-pen"></i> Modifier cette infrastructure</a>';
    }
    html += '</div>';
    return html;
  }'''

if "Modifier cette infrastructure" in contenu:
    resultats.append("IGNORE : lien Modifier deja present dans la popup infra.")
elif ancien_popup in contenu:
    contenu = contenu.replace(ancien_popup, nouveau_popup, 1)
    resultats.append("OK : lien 'Modifier cette infrastructure' ajoute a la popup.")
else:
    resultats.append("ERREUR : fonction construirePopupInfra introuvable telle quelle.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))