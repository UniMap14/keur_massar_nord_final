CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService"
nouveau_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale"

if nouveau_import_modeles in contenu:
    print("DEJA FAIT : import deja present.")
elif ancre_import_modeles in contenu:
    contenu = contenu.replace(ancre_import_modeles, nouveau_import_modeles, 1)
    changements += 1
    print("OK : import DeclarationFiscale ajoute.")
else:
    print("ERREUR : ligne d'import des modeles introuvable.")

ancre_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm"
nouveau_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm"

if ancre_import_forms in contenu:
    contenu = contenu.replace(ancre_import_forms, nouveau_import_forms, 1)
    changements += 1
    print("OK : import DeclarationFiscaleForm ajoute.")
elif nouveau_import_forms in contenu:
    print("DEJA FAIT : import deja present.")
else:
    print("ERREUR : ligne d'import des formulaires introuvable.")

AJOUT_VUES = '''

@login_required
def declarations_liste_view(request):
    """Liste des declarations fiscales deposees par le citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    declarations = []
    if profil:
        declarations = (
            DeclarationFiscale.objects.filter(contribuable=profil.contribuable)
            .select_related("parcelle", "type_taxe")
            .order_by("-date_declaration")
        )

    return render(request, "citoyens/espace/declarations_liste.html", {
        "declarations": declarations,
        "citoyen": citoyen,
        "active_section": "declarations",
    })


@login_required
def declaration_creer_view(request):
    """Formulaire de depot d'une nouvelle declaration fiscale."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None or profil.contribuable.proprietaire is None:
        messages.error(
            request,
            "Votre compte n'est pas encore relié à un dossier fiscal complet. "
            "Contactez la mairie pour effectuer une déclaration."
        )
        return redirect("citoyen_espace")

    parcelles_qs = Parcelle.objects.filter(proprietaire=profil.contribuable.proprietaire)

    if request.method == "POST":
        form = DeclarationFiscaleForm(request.POST, request.FILES, parcelles_qs=parcelles_qs)
        if form.is_valid():
            declaration = form.save(commit=False)
            declaration.contribuable = profil.contribuable
            declaration.save()
            messages.success(
                request,
                "Votre déclaration a bien été soumise. Elle sera examinée par un agent "
                "et donnera lieu à l'émission de votre taxation."
            )
            return redirect("citoyen_declarations")
    else:
        form = DeclarationFiscaleForm(parcelles_qs=parcelles_qs)

    return render(request, "citoyens/espace/declaration_form.html", {
        "form": form,
        "citoyen": citoyen,
        "active_section": "declarations",
    })
'''

if "def declarations_liste_view" in contenu:
    print("DEJA FAIT : vues deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT_VUES)
    changements += 1
    print("OK : 2 nouvelles vues ajoutees a la fin du fichier.")

print(f"\n=== {changements} changement(s) enregistres. ===")