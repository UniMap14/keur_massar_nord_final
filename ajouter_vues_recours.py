CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale"
nouveau_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal"

if nouveau_import_modeles in contenu:
    print("DEJA FAIT : import RecoursFiscal deja present.")
elif ancre_import_modeles in contenu:
    contenu = contenu.replace(ancre_import_modeles, nouveau_import_modeles, 1)
    changements += 1
    print("OK : import RecoursFiscal ajoute.")
else:
    print("ERREUR : ligne d'import des modeles introuvable.")

ancre_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm"
nouveau_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm"

if nouveau_import_forms in contenu:
    print("DEJA FAIT : import RecoursFiscalForm deja present.")
elif ancre_import_forms in contenu:
    contenu = contenu.replace(ancre_import_forms, nouveau_import_forms, 1)
    changements += 1
    print("OK : import RecoursFiscalForm ajoute.")
else:
    print("ERREUR : ligne d'import des formulaires introuvable.")

AJOUT = '''

@login_required
def recours_liste_view(request):
    """Liste des recours/redressements fiscaux deposes par le citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    recours_liste = []
    if profil:
        recours_liste = (
            RecoursFiscal.objects.filter(contribuable=profil.contribuable)
            .select_related("taxation", "taxation__type_taxe", "taxation__parcelle")
            .order_by("-date_soumission")
        )

    return render(request, "citoyens/espace/recours_liste.html", {
        "recours_liste": recours_liste,
        "citoyen": citoyen,
        "active_section": "recours",
    })


@login_required
def recours_creer_view(request, taxation_pk):
    """Depot d'un recours (niveau 1) sur une taxation precise."""
    from foncier.models import Taxation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    taxation = get_object_or_404(Taxation, pk=taxation_pk, contribuable=profil.contribuable)

    if request.method == "POST":
        form = RecoursFiscalForm(request.POST, request.FILES)
        if form.is_valid():
            recours = form.save(commit=False)
            recours.taxation = taxation
            recours.contribuable = profil.contribuable
            recours.niveau = RecoursFiscal.NIVEAU_RECOURS
            recours.save()
            messages.success(request, "Votre contestation a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_recours_liste")
    else:
        form = RecoursFiscalForm()

    return render(request, "citoyens/espace/recours_form.html", {
        "form": form,
        "taxation": taxation,
        "citoyen": citoyen,
        "active_section": "recours",
        "est_redressement": False,
    })


@login_required
def recours_redressement_creer_view(request, recours_pk):
    """Depot d'un redressement (niveau 2) suite au rejet d'un recours."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    recours_precedent = get_object_or_404(
        RecoursFiscal,
        pk=recours_pk,
        contribuable=profil.contribuable,
        niveau=RecoursFiscal.NIVEAU_RECOURS,
        statut=RecoursFiscal.STATUT_REJETE,
    )

    if request.method == "POST":
        form = RecoursFiscalForm(request.POST, request.FILES)
        if form.is_valid():
            redressement = form.save(commit=False)
            redressement.taxation = recours_precedent.taxation
            redressement.contribuable = profil.contribuable
            redressement.niveau = RecoursFiscal.NIVEAU_REDRESSEMENT
            redressement.recours_precedent = recours_precedent
            redressement.save()
            messages.success(request, "Votre demande de redressement a bien été soumise.")
            return redirect("citoyen_recours_liste")
    else:
        form = RecoursFiscalForm()

    return render(request, "citoyens/espace/recours_form.html", {
        "form": form,
        "taxation": recours_precedent.taxation,
        "citoyen": citoyen,
        "active_section": "recours",
        "est_redressement": True,
        "recours_precedent": recours_precedent,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def recours_liste_view" in contenu_a_jour:
    print("DEJA FAIT : vues recours deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : 3 vues recours ajoutees a la fin du fichier.")

print(f"\n=== {changements} changement(s) enregistres. ===")