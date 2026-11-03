# -*- coding: utf-8 -*-
"""
python ajouter_cfpb_cel_html.py

Patche le template foncier/templates/foncier/fiscalite.html :
  - ajoute les options CFPB et CEL-VL dans le select du simulateur
  - ajoute les champs conditionnels specifiques (type de batiment,
    residence principale, regime d'occupation)
  - met a jour le JS (bascule des champs, labels, et rendu du resultat
    pour les 2 nouveaux types + affichage generalise du detail de calcul
    pour TOUS les types, pas seulement l'IR)

Methode "tout ou rien" (voir ajouter_taxes_cfpb_cel.py pour le detail).
Independant du backend : peut etre lance avant ou apres
ajouter_taxes_cfpb_cel.py, mais le simulateur ne fonctionnera pour
CFPB/CEL-VL que lorsque les DEUX scripts auront reussi.
"""
import io

chemin = "foncier/templates/foncier/fiscalite.html"

edits = []

# ---------------------------------------------------------------------------
# 1) Nouvelles options dans le <select>
# ---------------------------------------------------------------------------
edits.append((
"""            <select id="simType" name="type_simulation">
              <option value="ir">Impôt sur le Revenu (IR) — Particulier</option>
              <option value="is">Impôt sur les Sociétés (IS) — Entreprise</option>
              <option value="tva">TVA — 18%</option>
              <option value="cgu">Contribution Globale Unique (CGU)</option>
            </select>""",
"""            <select id="simType" name="type_simulation">
              <option value="ir">Impôt sur le Revenu (IR) — Particulier</option>
              <option value="is">Impôt sur les Sociétés (IS) — Entreprise</option>
              <option value="tva">TVA — 18%</option>
              <option value="cgu">Contribution Globale Unique (CGU)</option>
              <option value="cfpb">Contribution Foncière des Propriétés Bâties (CFPB)</option>
              <option value="cel_vl">Contribution Économique Locale — Valeur Locative (CEL-VL)</option>
            </select>"""
))

# ---------------------------------------------------------------------------
# 2) Nouveaux champs conditionnels, juste avant le bouton Calculer
# ---------------------------------------------------------------------------
edits.append((
"""        <div class="sim-field" id="champ-secteur" style="display:none;">
          <label for="simSecteur">Secteur d'activité</label>
          <div class="sim-input-wrap">
            <i class="fa-solid fa-shop"></i>
            <select id="simSecteur" name="secteur_activite">
              <option value="bien">Vente / livraison de biens (commerce)</option>
              <option value="service">Prestation de services</option>
            </select>
          </div>
        </div>

        <button type="button" class="sim-btn" id="btnCalculer">""",
"""        <div class="sim-field" id="champ-secteur" style="display:none;">
          <label for="simSecteur">Secteur d'activité</label>
          <div class="sim-input-wrap">
            <i class="fa-solid fa-shop"></i>
            <select id="simSecteur" name="secteur_activite">
              <option value="bien">Vente / livraison de biens (commerce)</option>
              <option value="service">Prestation de services</option>
            </select>
          </div>
        </div>

        <div class="sim-field" id="champ-cfpb-secteur" style="display:none;">
          <label for="simCfpbSecteur">Type de bâtiment</label>
          <div class="sim-input-wrap">
            <i class="fa-solid fa-building"></i>
            <select id="simCfpbSecteur" name="cfpb_secteur">
              <option value="standard">Immeuble / bâtiment standard (5%)</option>
              <option value="usine">Usine / établissement industriel (7,5%)</option>
            </select>
          </div>
        </div>

        <div class="sim-field" id="champ-cfpb-residence" style="display:none;">
          <label for="simCfpbResidence" style="display:flex;align-items:center;gap:8px;cursor:pointer;font-weight:normal;">
            <input type="checkbox" id="simCfpbResidence" name="cfpb_residence_principale" style="width:auto;margin:0;">
            C'est ma résidence principale (abattement 500 000 FCFA)
          </label>
        </div>

        <div class="sim-field" id="champ-cel-regime" style="display:none;">
          <label for="simCelRegime">Régime d'occupation</label>
          <div class="sim-input-wrap">
            <i class="fa-solid fa-key"></i>
            <select id="simCelRegime" name="cel_vl_regime">
              <option value="loue">Local loué ou mis à disposition gratuitement (15%)</option>
              <option value="bilan">Local inscrit à l'actif du bilan (20%)</option>
            </select>
          </div>
        </div>

        <button type="button" class="sim-btn" id="btnCalculer">"""
))

# ---------------------------------------------------------------------------
# 3) JS : bascule des champs + labels (updateSimForm)
# ---------------------------------------------------------------------------
edits.append((
"""function updateSimForm() {
  const type = document.getElementById('simType').value;
  const labelRevenu = document.getElementById('labelRevenu');

  document.getElementById('champ-ca-is').style.display = (type === 'is') ? '' : 'none';
  document.getElementById('champ-situation').style.display = (type === 'ir') ? '' : 'none';
  document.getElementById('champ-enfants').style.display = (type === 'ir') ? '' : 'none';
  document.getElementById('champ-secteur').style.display = (type === 'cgu') ? '' : 'none';

  const labels = {
    ir: "Revenu net imposable annuel (FCFA)",
    is: "Bénéfice imposable annuel (FCFA)",
    tva: "Chiffre d'affaires HT annuel (FCFA)",
    cgu: "Chiffre d'affaires TTC annuel (FCFA)"
  };
  labelRevenu.textContent = labels[type] || "Revenu annuel (FCFA)";

  resetResult();
}""",
"""function updateSimForm() {
  const type = document.getElementById('simType').value;
  const labelRevenu = document.getElementById('labelRevenu');

  document.getElementById('champ-ca-is').style.display = (type === 'is') ? '' : 'none';
  document.getElementById('champ-situation').style.display = (type === 'ir') ? '' : 'none';
  document.getElementById('champ-enfants').style.display = (type === 'ir') ? '' : 'none';
  document.getElementById('champ-secteur').style.display = (type === 'cgu') ? '' : 'none';
  document.getElementById('champ-cfpb-secteur').style.display = (type === 'cfpb') ? '' : 'none';
  document.getElementById('champ-cfpb-residence').style.display = (type === 'cfpb') ? '' : 'none';
  document.getElementById('champ-cel-regime').style.display = (type === 'cel_vl') ? '' : 'none';

  const labels = {
    ir: "Revenu net imposable annuel (FCFA)",
    is: "Bénéfice imposable annuel (FCFA)",
    tva: "Chiffre d'affaires HT annuel (FCFA)",
    cgu: "Chiffre d'affaires TTC annuel (FCFA)",
    cfpb: "Valeur locative annuelle (FCFA)",
    cel_vl: "Valeur locative annuelle (FCFA)"
  };
  labelRevenu.textContent = labels[type] || "Revenu annuel (FCFA)";

  resetResult();
}"""
))

# ---------------------------------------------------------------------------
# 4) JS : rendu du resultat (afficherResultat) - ajout cfpb/cel_vl +
#    affichage generalise du detail de calcul pour tous les types
# ---------------------------------------------------------------------------
edits.append((
"""function afficherResultat(data) {
  const box = document.getElementById('simResult');
  let html = '';

  if (data.type === 'ir') {
    html += ligneResultat('Revenu net imposable', fmtFCFA(data.revenu_net_imposable));
    html += ligneResultat('Nombre de parts (quotient familial)', data.parts);
    html += ligneResultat('Quotient (par part)', fmtFCFA(data.quotient_par_part));
    html += ligneResultat('<strong>Impôt sur le revenu estimé</strong>', fmtFCFA(data.impot), 'tax');
    html += ligneResultat('Taux effectif d\\'imposition', data.taux_effectif + '%');
    html += ligneResultat('Revenu net après impôt', fmtFCFA(data.net_apres_impot), 'total');

    if (data.detail_tranches && data.detail_tranches.length) {
      html += '<div class="bareme-visual"><p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;font-weight:600;">Détail par tranche (sur le quotient)</p>';
      data.detail_tranches.forEach(function (t) {
        html += '<div class="bareme-bar-wrap"><div class="bareme-bar-label"><span>' + t.tranche + '</span><span>' + t.taux + '% — ' + fmtFCFA(t.montant) + '</span></div>' +
                '<div class="bareme-bar-track"><div class="bareme-bar-fill" style="width:100%"></div></div></div>';
      });
      html += '</div>';
    }
  } else if (data.type === 'is') {
    html += ligneResultat('Bénéfice imposable', fmtFCFA(data.benefice_imposable));
    html += ligneResultat('Chiffre d\\'affaires HT (base IMF)', fmtFCFA(data.chiffre_affaires_ht));
    html += ligneResultat('IS calculé (30%)', fmtFCFA(data.is_calcule));
    html += ligneResultat('IMF calculé (0,5% du CA)', fmtFCFA(data.imf_calcule));
    html += ligneResultat('Régime appliqué', data.regime_applique);
    html += ligneResultat('<strong>Impôt final dû</strong>', fmtFCFA(data.impot), 'tax');
  } else if (data.type === 'tva') {
    html += ligneResultat('Chiffre d\\'affaires HT', fmtFCFA(data.chiffre_affaires_ht));
    html += ligneResultat('<strong>TVA due (18%)</strong>', fmtFCFA(data.impot), 'tax');
  } else if (data.type === 'cgu') {
    html += ligneResultat('Chiffre d\\'affaires TTC', fmtFCFA(data.chiffre_affaires_ttc));
    html += ligneResultat('Taux appliqué', data.taux_applique + '%');
    html += ligneResultat('<strong>CGU due</strong>', fmtFCFA(data.impot), 'tax');
    if (data.depasse_seuil_cgu) {
      html += '<div class="warn-band" style="margin-top:16px;"><i class="fa-solid fa-triangle-exclamation"></i>' +
              '<p>Votre chiffre d\\'affaires dépasse le seuil de ' + fmtFCFA(data.seuil_cgu) + ' autorisé pourla CGU. Vous relevez probablement du régime réel (IS/TVA).</p></div>';
    }
  }

  html += '<p style="font-size:12px;color:var(--text-muted);margin-top:20px;padding-top:16px;border-top:1px dashed var(--border);">' + data.reference + '</p>';

  box.innerHTML = html;
  box.style.display = 'block';
}""",
"""function afficherResultat(data) {
  const box = document.getElementById('simResult');
  let html = '';

  if (data.type === 'ir') {
    html += ligneResultat('Revenu net imposable', fmtFCFA(data.revenu_net_imposable));
    html += ligneResultat('Nombre de parts (quotient familial)', data.parts);
    html += ligneResultat('Quotient (par part)', fmtFCFA(data.quotient_par_part));
    html += ligneResultat('<strong>Impôt sur le revenu estimé</strong>', fmtFCFA(data.impot), 'tax');
    html += ligneResultat('Taux effectif d\\'imposition', data.taux_effectif + '%');
    html += ligneResultat('Revenu net après impôt', fmtFCFA(data.net_apres_impot), 'total');
  } else if (data.type === 'is') {
    html += ligneResultat('Bénéfice imposable', fmtFCFA(data.benefice_imposable));
    html += ligneResultat('Chiffre d\\'affaires HT (base IMF)', fmtFCFA(data.chiffre_affaires_ht));
    html += ligneResultat('IS calculé (30%)', fmtFCFA(data.is_calcule));
    html += ligneResultat('IMF calculé (0,5% du CA)', fmtFCFA(data.imf_calcule));
    html += ligneResultat('Régime appliqué', data.regime_applique);
    html += ligneResultat('<strong>Impôt final dû</strong>', fmtFCFA(data.impot), 'tax');
  } else if (data.type === 'tva') {
    html += ligneResultat('Chiffre d\\'affaires HT', fmtFCFA(data.chiffre_affaires_ht));
    html += ligneResultat('<strong>TVA due (18%)</strong>', fmtFCFA(data.impot), 'tax');
  } else if (data.type === 'cgu') {
    html += ligneResultat('Chiffre d\\'affaires TTC', fmtFCFA(data.chiffre_affaires_ttc));
    html += ligneResultat('Taux appliqué', data.taux_applique + '%');
    html += ligneResultat('<strong>CGU due</strong>', fmtFCFA(data.impot), 'tax');
    if (data.depasse_seuil_cgu) {
      html += '<div class="warn-band" style="margin-top:16px;"><i class="fa-solid fa-triangle-exclamation"></i>' +
              '<p>Votre chiffre d\\'affaires dépasse le seuil de ' + fmtFCFA(data.seuil_cgu) + ' autorisé pourla CGU. Vous relevez probablement du régime réel (IS/TVA).</p></div>';
    }
  } else if (data.type === 'cfpb') {
    html += ligneResultat('Valeur locative annuelle', fmtFCFA(data.valeur_locative));
    if (data.abattement && data.abattement > 0) {
      html += ligneResultat('Abattement résidence principale', '-' + fmtFCFA(data.abattement));
    }
    html += ligneResultat('Base imposable', fmtFCFA(data.base_imposable));
    html += ligneResultat('Taux appliqué', data.taux_applique + '%');
    html += ligneResultat('<strong>CFPB due</strong>', fmtFCFA(data.impot), 'tax');
  } else if (data.type === 'cel_vl') {
    html += ligneResultat('Valeur locative annuelle', fmtFCFA(data.valeur_locative));
    html += ligneResultat('Régime d\\'occupation', data.regime_cel);
    html += ligneResultat('Taux appliqué', data.taux_applique + '%');
    html += ligneResultat('<strong>CEL-VL due</strong>', fmtFCFA(data.impot), 'tax');
  }

  if (data.detail_tranches && data.detail_tranches.length) {
    html += '<div class="bareme-visual"><p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;font-weight:600;">Détail du calcul</p>';
    data.detail_tranches.forEach(function (t) {
      html += '<div class="bareme-bar-wrap"><div class="bareme-bar-label"><span>' + t.tranche + '</span><span>' + (t.taux ? (t.taux + '% — ') : '') + fmtFCFA(t.montant) + '</span></div>' +
              '<div class="bareme-bar-track"><div class="bareme-bar-fill" style="width:100%"></div></div></div>';
    });
    html += '</div>';
  }

  html += '<p style="font-size:12px;color:var(--text-muted);margin-top:20px;padding-top:16px;border-top:1px dashed var(--border);">' + data.reference + '</p>';

  box.innerHTML = html;
  box.style.display = 'block';
}"""
))


def lire(c):
    with io.open(c, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(c, contenu):
    with io.open(c, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)


contenu = lire(chemin)
erreurs = []
for i, (old, new) in enumerate(edits):
    n = contenu.count(old)
    if n != 1:
        erreurs.append(f"modification #{i + 1}: trouve {n} fois (attendu 1)")

if erreurs:
    print("ECHEC - AUCUNE modification appliquee (fichier inchange). Problemes :")
    for e in erreurs:
        print(" -", e)
    print("\nEnvoyez-moi l'extrait exact concerne pour que j'ajuste l'ancre.")
else:
    for old, new in edits:
        contenu = contenu.replace(old, new)
    ecrire(chemin, contenu)
    print("OK - toutes les modifications appliquees a fiscalite.html.")
    print("Rechargez la page (Ctrl+F5) une fois le backend (forms.py/views.py) aussi a jour.")