# -*- coding: utf-8 -*-
"""
Corrige le bouton "Enregistrer" qui ne fait rien sur la page de
traitement d'une demande (dashboard_demande_detail).

Cause : TraitementDemandeForm (foncier/dashboard_views.py) exige le
champ 'statut_paiement' (obligatoire cote modele, pas de blank=True),
mais le template demande_detail.html ne l'affiche jamais. A chaque
soumission, Django rejette le formulaire pour champ manquant, et comme
les erreurs globales ne sont pas affichees, la page se recharge a
l'identique -> on dirait que rien ne se passe.

Ce script :
  1. Ajoute le champ "Statut du paiement" dans le formulaire affiche.
  2. Affiche aussi les erreurs globales du formulaire (non_field_errors),
     pour que toute future erreur de validation soit visible au lieu
     d'etre silencieuse.

Idempotent : si deja applique, ne touche a rien.
"""
import io

CHEMIN = r"foncier\templates\dashboard\demande_detail.html"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

modifie = False

# --- 1. Afficher les erreurs globales du formulaire juste apres le csrf_token ---
ancre_csrf = "{% csrf_token %}"
if "{{ form.non_field_errors }}" not in contenu:
    remplacement = (
        "{% csrf_token %}\n"
        "      {% if form.non_field_errors %}\n"
        "        <div class=\"form-field\" style=\"color:#c0392b; font-weight:600;\">\n"
        "          {{ form.non_field_errors }}\n"
        "        </div>\n"
        "      {% endif %}"
    )
    if ancre_csrf in contenu:
        contenu = contenu.replace(ancre_csrf, remplacement, 1)
        modifie = True

# --- 2. Ajouter le champ statut_paiement, juste apres le champ statut ---
ancre_statut = (
    "        {{ form.statut.errors }}\n"
    "      </div>\n"
)
bloc_statut_paiement = (
    "      <div class=\"form-field\">\n"
    "        <label for=\"{{ form.statut_paiement.id_for_label }}\">"
    "<i class=\"fa-solid fa-money-check-dollar\"></i> Statut du paiement</label>\n"
    "        {{ form.statut_paiement }}\n"
    "        {{ form.statut_paiement.errors }}\n"
    "      </div>\n"
)
if "form.statut_paiement" not in contenu:
    if ancre_statut not in contenu:
        raise SystemExit(
            "ERREUR : ancre du champ 'statut' introuvable dans le template. "
            "Le fichier a peut-etre deja ete modifie manuellement — a verifier."
        )
    contenu = contenu.replace(ancre_statut, ancre_statut + bloc_statut_paiement, 1)
    modifie = True

if modifie:
    with io.open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("OK : template demande_detail.html corrige (champ statut_paiement ajoute).")
else:
    print("OK : deja a jour, rien a faire.")