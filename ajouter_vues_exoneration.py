CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal"
nouveau_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal, DemandeExoneration"

if nouveau_import_modeles in contenu:
    print("DEJA FAIT : import DemandeExoneration deja present.")
elif ancre_import_modeles in contenu:
    contenu = contenu.replace(ancre_import_modeles, nouveau_import_modeles, 1)
    changements += 1
    print("OK : import DemandeExoneration ajoute.")
else:
    print("ERREUR : ligne d'import des modeles introuvable.")

ancre_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm"
nouveau_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm, DemandeExonerationForm"

if nouveau_import_forms in contenu:
    print("DEJA FAIT : import DemandeExonerationForm deja present.")
elif ancre_import_forms in contenu:
    contenu = contenu.replace(ancre_import_forms, nouveau_import_forms, 1)
    changements += 1
    print("OK : import DemandeExonerationForm ajoute.")
else:
    print("ERREUR : ligne d'import des formulaires introuvable.")

AJOUT = '''

@login_required
def exoneration_liste_view(request):
    """Liste des demandes d'exoneration fiscale deposees par le citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    demandes = []
    if profil:
        demandes = (
            DemandeExoneration.objects.filter(contribuable=profil.contribuable)
            .select_related("parcelle")
            .order_by("-date_soumission")
        )

    return render(request, "citoyens/espace/exoneration_liste.html", {
        "demandes": demandes,
        "citoyen": citoyen,
        "active_section": "exonerations",
    })


@login_required
def exoneration_creer_view(request, parcelle_pk):
    """Depot d'une demande d'exoneration fiscale pour une parcelle precise."""
    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    parcelles_qs = Parcelle.objects.filter(taxations__contribuable=profil.contribuable)
    if profil.contribuable.proprietaire is not None:
        parcelles_qs = parcelles_qs | Parcelle.objects.filter(proprietaire=profil.contribuable.proprietaire)
    parcelle = get_object_or_404(parcelles_qs.distinct(), pk=parcelle_pk)

    if request.method == "POST":
        form = DemandeExonerationForm(request.POST, request.FILES)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.contribuable = profil.contribuable
            demande.parcelle = parcelle
            demande.save()
            messages.success(request, "Votre demande d'exonération a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_exoneration_liste")
    else:
        form = DemandeExonerationForm()

    return render(request, "citoyens/espace/exoneration_form.html", {
        "form": form,
        "parcelle": parcelle,
        "citoyen": citoyen,
        "active_section": "exonerations",
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def exoneration_liste_view" in contenu_a_jour:
    print("DEJA FAIT : vues deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : 2 vues exoneration ajoutees a la fin du fichier.")

print(f"\n=== {changements} changement(s) enregistres. ===")