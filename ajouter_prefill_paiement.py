CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    else:
        form = PaiementEnLigneForm()

    return render(request, "citoyens/espace/payer_taxation.html", {
        "taxation": taxation,
        "form": form,
    })'''

nouveau = '''    else:
        # Pre-remplit avec le compte de paiement enregistre dans le
        # profil du citoyen, s'il en a un (moins de friction que de
        # retaper operateur + numero a chaque paiement).
        initial = {}
        citoyen = getattr(request.user, "citoyen", None)
        if citoyen is not None:
            if citoyen.operateur_paiement:
                initial["operateur"] = citoyen.operateur_paiement
            if citoyen.telephone:
                initial["telephone"] = citoyen.telephone
        form = PaiementEnLigneForm(initial=initial)

    return render(request, "citoyens/espace/payer_taxation.html", {
        "taxation": taxation,
        "form": form,
    })'''

if "Pre-remplit avec le compte de paiement enregistre" in contenu:
    print("DEJA FAIT : deja modifie.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : pre-remplissage du paiement ajoute.")
else:
    print("ERREUR : bloc exact introuvable.")