CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None or profil.contribuable.proprietaire is None:
        messages.error(
            request,
            "Votre compte n'est pas encore relié à un dossier fiscal complet. "
            "Contactez la mairie pour effectuer une déclaration."
        )
        return redirect("citoyen_espace")

    parcelles_qs = Parcelle.objects.filter(proprietaire=profil.contribuable.proprietaire)'''

nouveau = '''    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(
            request,
            "Votre compte n'est pas encore relié à un dossier fiscal. "
            "Contactez la mairie pour effectuer une déclaration."
        )
        return redirect("citoyen_espace")

    # Les parcelles "a soi" sont celles deja liees via une taxation
    # existante (fonctionne aussi pour les comptes simules sans
    # Proprietaire officiellement rattache), plus celles du Proprietaire
    # lie le cas echeant (dossier reel).
    parcelles_qs = Parcelle.objects.filter(taxations__contribuable=profil.contribuable)
    if profil.contribuable.proprietaire is not None:
        parcelles_qs = parcelles_qs | Parcelle.objects.filter(proprietaire=profil.contribuable.proprietaire)
    parcelles_qs = parcelles_qs.distinct()'''

if nouveau in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : recherche des parcelles corrigee (fonctionne meme sans Proprietaire lie).")
else:
    print("ERREUR : bloc exact introuvable.")