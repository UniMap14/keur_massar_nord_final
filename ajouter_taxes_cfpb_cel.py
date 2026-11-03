# -*- coding: utf-8 -*-
"""
python ajouter_taxes_cfpb_cel.py

A lancer depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn
(pas besoin de "manage.py shell" : ce script ne fait que modifier du texte,
aucun acces a Django).

Ajoute deux nouveaux types d'impot au simulateur fiscal, avec leurs sources :
  - CFPB  : Contribution Fonciere des Proprietes Baties
            5 % (ou 7,5 % pour une usine) de la valeur locative,
            abattement de 500 000 FCFA si residence principale (Art. 329-334 CGI)
  - CEL-VL: Contribution Economique Locale - Valeur Locative
            15 % (local loue/gratuit) ou 20 % (actif du bilan) (Art. 330 CGI)

Ameliore aussi l'affichage du detail de calcul pour IS, TVA et CGU (en plus
de l'IR qui l'avait deja), pour repondre a la demande "afficher le detail
du calcul".

Fichiers modifies :
  - foncier/forms.py
  - foncier/views.py

Methode "tout ou rien" : chaque ancre doit exister EXACTEMENT une fois dans
son fichier. Si une seule ne correspond pas (fichier different de ce qui a
ete lu), RIEN n'est modifie et le script affiche precisement laquelle, pour
qu'on puisse me renvoyer l'extrait exact plutot que de risquer une
modification incorrecte.
"""
import io

edits = {}

# ---------------------------------------------------------------------------
# foncier/forms.py
# ---------------------------------------------------------------------------
edits["foncier/forms.py"] = []

# Edit 1 : ajouter les 2 nouveaux types dans TYPE_CHOICES
edits["foncier/forms.py"].append((
"""    TYPE_CHOICES = [
        ("ir", "Impôt sur le Revenu (IR) — Particulier"),
        ("is", "Impôt sur les Sociétés (IS) — Entreprise"),
        ("tva", "TVA — 18 %"),
        ("cgu", "Contribution Globale Unique (CGU) — Petite entreprise"),
    ]""",
"""    TYPE_CHOICES = [
        ("ir", "Impôt sur le Revenu (IR) — Particulier"),
        ("is", "Impôt sur les Sociétés (IS) — Entreprise"),
        ("tva", "TVA — 18 %"),
        ("cgu", "Contribution Globale Unique (CGU) — Petite entreprise"),
        ("cfpb", "Contribution Foncière des Propriétés Bâties (CFPB)"),
        ("cel_vl", "Contribution Économique Locale — Valeur Locative (CEL-VL)"),
    ]"""
))

# Edit 2 : ajouter les champs specifiques CFPB / CEL-VL apres secteur_activite
edits["foncier/forms.py"].append((
"""    secteur_activite = forms.ChoiceField(choices=SECTEUR_CHOICES, required=False, initial="bien", label="Secteur d'activité (CGU)")""",
"""    secteur_activite = forms.ChoiceField(choices=SECTEUR_CHOICES, required=False, initial="bien", label="Secteur d'activité (CGU)")

    CFPB_SECTEUR_CHOICES = [
        ("standard", "Immeuble / bâtiment standard (5 %)"),
        ("usine", "Usine / établissement industriel (7,5 %)"),
    ]
    cfpb_secteur = forms.ChoiceField(choices=CFPB_SECTEUR_CHOICES, required=False, initial="standard", label="Type de bâtiment (CFPB)")
    cfpb_residence_principale = forms.BooleanField(required=False, initial=False, label="C'est ma résidence principale (abattement 500 000 FCFA)")

    CEL_VL_REGIME_CHOICES = [
        ("loue", "Local loué ou mis à disposition gratuitement (15 %)"),
        ("bilan", "Local inscrit à l'actif du bilan de l'entreprise (20 %)"),
    ]
    cel_vl_regime = forms.ChoiceField(choices=CEL_VL_REGIME_CHOICES, required=False, initial="loue", label="Régime d'occupation (CEL-VL)")"""
))

# Edit 3 : valeurs par defaut dans clean()
edits["foncier/forms.py"].append((
"""        if not cleaned.get("secteur_activite"): cleaned["secteur_activite"] = "bien"
        return cleaned""",
"""        if not cleaned.get("secteur_activite"): cleaned["secteur_activite"] = "bien"
        if not cleaned.get("cfpb_secteur"): cleaned["cfpb_secteur"] = "standard"
        cleaned["cfpb_residence_principale"] = bool(cleaned.get("cfpb_residence_principale"))
        if not cleaned.get("cel_vl_regime"): cleaned["cel_vl_regime"] = "loue"
        return cleaned"""
))

# ---------------------------------------------------------------------------
# foncier/views.py
# ---------------------------------------------------------------------------
edits["foncier/views.py"] = []

edits["foncier/views.py"].append((
"""        elif type_sim == "is":
            benefice = revenu; ca_ht = data.get("chiffre_affaires_is") or benefice
            is_calcule = benefice * Decimal("0.30") if benefice > 0 else Decimal("0")
            imf = ca_ht * Decimal("0.005"); imf = max(Decimal("500000"), min(imf, Decimal("5000000")))
            deficitaire = benefice <= 0; imf_applicable = deficitaire or is_calcule < imf
            impot_final = imf if imf_applicable else is_calcule
            resultat.update({"benefice_imposable": _arrondi(benefice), "chiffre_affaires_ht": _arrondi(ca_ht), "is_calcule": _arrondi(is_calcule), "imf_calcule": _arrondi(imf), "regime_applique": "IMF" if imf_applicable else "IS", "impot": _arrondi(impot_final), "reference": "IS = 30 % du bénéfice imposable. Impôt Minimum Forfaitaire (IMF) = 0,5 % du CA HT si déficit ou si IS < IMF (plancher 500 000 FCFA, plafond 5 000 000 FCFA)."})
        elif type_sim == "tva":
            tva = revenu * Decimal("0.18")
            resultat.update({"chiffre_affaires_ht": _arrondi(revenu), "impot": _arrondi(tva), "reference": "TVA au taux normal de 18 % (Livre II du CGI, Directive UEMOA n°02/98/CM). Taux réduit de 10 % pour l'hôtellerie/tourisme non couvert par cette simulation."})
        elif type_sim == "cgu":
            secteur = data["secteur_activite"]; est_bien = secteur == "bien"
            taux = Decimal("0.02") if est_bien else Decimal("0.05")
            plancher = Decimal("25000") if est_bien else Decimal("30000")
            seuil = Decimal("50000000") if est_bien else Decimal("25000000")
            cgu = max(revenu * taux, plancher); depasse_seuil = revenu > seuil
            resultat.update({"chiffre_affaires_ttc": _arrondi(revenu), "taux_applique": float(taux)*100, "impot": _arrondi(cgu), "depasse_seuil_cgu": depasse_seuil, "seuil_cgu": _arrondi(seuil), "reference": f"CGU = {float(taux)*100:.0f} % du CA TTC ({'biens' if est_bien else 'services'}), plancher {int(plancher):,} FCFA. Régime réservé aux CA ≤ {int(seuil):,} FCFA.".replace(",", " ")})
        else:
            return JsonResponse({"ok": False, "errors": "Type d'impôt inconnu."}, status=400)
        return JsonResponse(resultat)""",
"""        elif type_sim == "is":
            benefice = revenu; ca_ht = data.get("chiffre_affaires_is") or benefice
            is_calcule = benefice * Decimal("0.30") if benefice > 0 else Decimal("0")
            imf = ca_ht * Decimal("0.005"); imf = max(Decimal("500000"), min(imf, Decimal("5000000")))
            deficitaire = benefice <= 0; imf_applicable = deficitaire or is_calcule < imf
            impot_final = imf if imf_applicable else is_calcule
            detail_is = [
                {"tranche": "IS = 30 % du bénéfice imposable", "taux": 30.0, "montant": _arrondi(is_calcule)},
                {"tranche": "IMF = 0,5 % du CA HT (plancher 500 000, plafond 5 000 000)", "taux": 0.5, "montant": _arrondi(imf)},
            ]
            resultat.update({"benefice_imposable": _arrondi(benefice), "chiffre_affaires_ht": _arrondi(ca_ht), "is_calcule": _arrondi(is_calcule), "imf_calcule": _arrondi(imf), "regime_applique": "IMF" if imf_applicable else "IS", "impot": _arrondi(impot_final), "detail_tranches": detail_is, "reference": "IS = 30 % du bénéfice imposable. Impôt Minimum Forfaitaire (IMF) = 0,5 % du CA HT si déficit ou si IS < IMF (plancher 500 000 FCFA, plafond 5 000 000 FCFA)."})
        elif type_sim == "tva":
            tva = revenu * Decimal("0.18")
            detail_tva = [{"tranche": "Chiffre d'affaires HT x 18 %", "taux": 18.0, "montant": _arrondi(tva)}]
            resultat.update({"chiffre_affaires_ht": _arrondi(revenu), "impot": _arrondi(tva), "detail_tranches": detail_tva, "reference": "TVA au taux normal de 18 % (Livre II du CGI, Directive UEMOA n°02/98/CM). Taux réduit de 10 % pour l'hôtellerie/tourisme non couvert par cette simulation."})
        elif type_sim == "cgu":
            secteur = data["secteur_activite"]; est_bien = secteur == "bien"
            taux = Decimal("0.02") if est_bien else Decimal("0.05")
            plancher = Decimal("25000") if est_bien else Decimal("30000")
            seuil = Decimal("50000000") if est_bien else Decimal("25000000")
            cgu = max(revenu * taux, plancher); depasse_seuil = revenu > seuil
            detail_cgu = [{"tranche": f"CA TTC x {float(taux)*100:.0f} % (plancher {int(plancher):,} FCFA)".replace(",", " "), "taux": float(taux)*100, "montant": _arrondi(cgu)}]
            resultat.update({"chiffre_affaires_ttc": _arrondi(revenu), "taux_applique": float(taux)*100, "impot": _arrondi(cgu), "depasse_seuil_cgu": depasse_seuil, "seuil_cgu": _arrondi(seuil), "detail_tranches": detail_cgu, "reference": f"CGU = {float(taux)*100:.0f} % du CA TTC ({'biens' if est_bien else 'services'}), plancher {int(plancher):,} FCFA. Régime réservé aux CA ≤ {int(seuil):,} FCFA.".replace(",", " ")})
        elif type_sim == "cfpb":
            secteur_cfpb = data["cfpb_secteur"]; est_usine = secteur_cfpb == "usine"
            taux = Decimal("0.075") if est_usine else Decimal("0.05")
            valeur_locative = revenu
            residence_principale = bool(data.get("cfpb_residence_principale"))
            abattement = Decimal("500000") if (residence_principale and not est_usine) else Decimal("0")
            abattement = min(abattement, valeur_locative)
            base_imposable = valeur_locative - abattement
            cfpb = base_imposable * taux
            libelle_bien = "usine / établissement industriel" if est_usine else "immeuble standard"
            detail_cfpb = []
            if abattement > 0:
                detail_cfpb.append({"tranche": "Abattement résidence principale", "taux": 0, "montant": -_arrondi(abattement)})
            detail_cfpb.append({"tranche": f"Base imposable x {float(taux)*100:.1f} %", "taux": float(taux)*100, "montant": _arrondi(cfpb)})
            resultat.update({"valeur_locative": _arrondi(valeur_locative), "abattement": _arrondi(abattement), "base_imposable": _arrondi(base_imposable), "taux_applique": float(taux)*100, "impot": _arrondi(cfpb), "detail_tranches": detail_cfpb, "reference": f"Contribution Foncière des Propriétés Bâties (CFPB) = {float(taux)*100:.1f} % de la valeur locative ({libelle_bien}), abattement de 500 000 FCFA si résidence principale du propriétaire (Art. 329-334 CGI). Constructions neuves exonérées jusqu'à la 6e année."})
        elif type_sim == "cel_vl":
            regime_cel = data["cel_vl_regime"]; est_bilan = regime_cel == "bilan"
            taux = Decimal("0.20") if est_bilan else Decimal("0.15")
            valeur_locative = revenu
            cel = valeur_locative * taux
            libelle_regime = "local inscrit à l'actif du bilan de l'entreprise" if est_bilan else "local loué ou mis à disposition gratuitement"
            detail_cel = [{"tranche": f"Valeur locative x {float(taux)*100:.0f} %", "taux": float(taux)*100, "montant": _arrondi(cel)}]
            resultat.update({"valeur_locative": _arrondi(valeur_locative), "taux_applique": float(taux)*100, "impot": _arrondi(cel), "detail_tranches": detail_cel, "regime_cel": "Actif du bilan" if est_bilan else "Loué / mis à disposition gratuitement", "reference": f"Contribution Économique Locale — Valeur Locative (CEL-VL) = {float(taux)*100:.0f} % de la valeur locative ({libelle_regime}), Art. 330 CGI. Déclaration avant le 31 janvier."})
        else:
            return JsonResponse({"ok": False, "errors": "Type d'impôt inconnu."}, status=400)
        return JsonResponse(resultat)"""
))

# ---------------------------------------------------------------------------
# Verification "tout ou rien", puis application
# ---------------------------------------------------------------------------
def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, contenu):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)


erreurs = []
contenus = {}
for chemin, paires in edits.items():
    contenu = lire(chemin)
    contenus[chemin] = contenu
    for i, (old, new) in enumerate(paires):
        n = contenu.count(old)
        if n != 1:
            erreurs.append(f"{chemin} - modification #{i + 1}: trouve {n} fois (attendu 1)")

if erreurs:
    print("ECHEC - AUCUNE modification appliquee (fichiers inchanges). Problemes :")
    for e in erreurs:
        print(" -", e)
    print("\nEnvoyez-moi l'extrait exact du fichier concerne pour que j'ajuste l'ancre.")
else:
    for chemin, paires in edits.items():
        contenu = contenus[chemin]
        for old, new in paires:
            contenu = contenu.replace(old, new)
        ecrire(chemin, contenu)
    print("OK - toutes les modifications appliquees (forms.py + views.py).")
    print("Le backend connait maintenant 'cfpb' et 'cel_vl', et IS/TVA/CGU renvoient")
    print("aussi un detail_tranches. Redemarrez le serveur (python manage.py runserver).")
    print("Prochaine etape : patcher le template fiscalite.html (select + champs + JS).")