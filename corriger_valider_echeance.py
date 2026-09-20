CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    if paiement.statut_paiement == "EN_ATTENTE":
        paiement.statut_paiement = "CONFIRME"
        paiement.save(update_fields=["statut_paiement"])
        messages.success(request, f"Paiement {paiement.numero_recu} validé — le reçu est maintenant disponible.")
    else:
        messages.info(request, "Ce paiement n'était pas en attente de validation.")

    return redirect("dashboard_paiement_list")'''

nouveau = '''    if paiement.statut_paiement == "EN_ATTENTE":
        paiement.statut_paiement = "CONFIRME"
        paiement.save(update_fields=["statut_paiement"])

        # Si ce paiement correspond a une echeance de plan de paiement,
        # la marque payee et termine le plan si c'etait la derniere.
        echeance = getattr(paiement, "echeance_origine", None)
        if echeance is not None:
            echeance.statut = "PAYEE"
            echeance.save(update_fields=["statut"])

            plan = echeance.plan
            if not plan.echeances.exclude(statut="PAYEE").exists():
                plan.statut = "TERMINE"
                plan.save(update_fields=["statut"])

        messages.success(request, f"Paiement {paiement.numero_recu} validé — le reçu est maintenant disponible.")
    else:
        messages.info(request, "Ce paiement n'était pas en attente de validation.")

    return redirect("dashboard_paiement_list")'''

if "echeance_origine" in contenu and "def dashboard_paiement_valider" in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : dashboard_paiement_valider met maintenant a jour l'echeance liee.")
else:
    print("ERREUR : bloc exact introuvable.")