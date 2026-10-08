CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal, DemandeExoneration, PlanPaiement"
nouveau_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal, DemandeExoneration, PlanPaiement, DemandeMorcellementFusion"

if nouveau_import_modeles in contenu:
    print("DEJA FAIT : import DemandeMorcellementFusion deja present.")
elif ancre_import_modeles in contenu:
    contenu = contenu.replace(ancre_import_modeles, nouveau_import_modeles, 1)
    changements += 1
    print("OK : import DemandeMorcellementFusion ajoute.")
else:
    print("ERREUR : ligne d'import des modeles introuvable.")

ancre_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm, DemandeExonerationForm, PlanPaiementForm"
nouveau_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm, DemandeExonerationForm, PlanPaiementForm, DemandeMorcellementFusionForm"

if nouveau_import_forms in contenu:
    print("DEJA FAIT : import DemandeMorcellementFusionForm deja present.")
elif ancre_import_forms in contenu:
    contenu = contenu.replace(ancre_import_forms, nouveau_import_forms, 1)
    changements += 1
    print("OK : import DemandeMorcellementFusionForm ajoute.")
else:
    print("ERREUR : ligne d'import des formulaires introuvable.")

AJOUT = '''

@login_required
def morcellement_fusion_liste_view(request):
    """Liste des demandes de morcellement/fusion du citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    demandes = (
        DemandeMorcellementFusion.objects.filter(demandeur=request.user)
        .prefetch_related("parcelles_concernees", "parcelles_resultantes")
        .order_by("-date_soumission")
    )

    return render(request, "citoyens/espace/morcellement_fusion_liste.html", {
        "demandes": demandes,
        "citoyen": citoyen,
        "active_section": "morcellement_fusion",
    })


@login_required
def morcellement_fusion_creer_view(request):
    """Depot d'une demande de morcellement ou de fusion de parcelle(s)."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    parcelles_qs = _parcelles_du_citoyen_qs(request.user)

    if request.method == "POST":
        form = DemandeMorcellementFusionForm(request.POST, request.FILES, parcelles_qs=parcelles_qs)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            form.save_m2m()
            messages.success(request, "Votre demande a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_morcellement_fusion_liste")
    else:
        form = DemandeMorcellementFusionForm(parcelles_qs=parcelles_qs)

    return render(request, "citoyens/espace/morcellement_fusion_form.html", {
        "form": form,
        "citoyen": citoyen,
        "active_section": "morcellement_fusion",
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def morcellement_fusion_liste_view" in contenu_a_jour:
    print("DEJA FAIT : vues deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : 2 vues morcellement/fusion ajoutees a la fin du fichier.")

print(f"\n=== {changements} changement(s) enregistres. ===")