CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_initial_1 = '''        form = ModifierProfilForm(request.POST, user=request.user, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "telephone": citoyen.telephone,
        })'''
nouveau_initial_1 = '''        form = ModifierProfilForm(request.POST, user=request.user, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "telephone": citoyen.telephone,
            "operateur_paiement": citoyen.operateur_paiement,
        })'''

ancien_initial_2 = '''        form = ModifierProfilForm(user=request.user, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "telephone": citoyen.telephone,
        })'''
nouveau_initial_2 = '''        form = ModifierProfilForm(user=request.user, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "telephone": citoyen.telephone,
            "operateur_paiement": citoyen.operateur_paiement,
        })'''

if "operateur_paiement" in contenu and "def modifier_profil_view" in contenu:
    print("DEJA FAIT : vue deja modifiee.")
else:
    if ancien_initial_1 in contenu:
        contenu = contenu.replace(ancien_initial_1, nouveau_initial_1, 1)
        changements += 1
        print("OK : operateur_paiement ajoute au 1er 'initial' (POST).")
    else:
        print("ERREUR : 1er bloc 'initial' introuvable.")

    if ancien_initial_2 in contenu:
        contenu = contenu.replace(ancien_initial_2, nouveau_initial_2, 1)
        changements += 1
        print("OK : operateur_paiement ajoute au 2e 'initial' (GET).")
    else:
        print("ERREUR : 2e bloc 'initial' introuvable.")

    ancien_save = '''            citoyen.telephone = form.cleaned_data["telephone"]
            citoyen.save()'''
    nouveau_save = '''            citoyen.telephone = form.cleaned_data["telephone"]
            citoyen.operateur_paiement = form.cleaned_data["operateur_paiement"]
            citoyen.save()'''

    if ancien_save in contenu:
        contenu = contenu.replace(ancien_save, nouveau_save, 1)
        changements += 1
        print("OK : sauvegarde de operateur_paiement ajoutee.")
    else:
        print("ERREUR : bloc de sauvegarde introuvable.")

    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")