CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal, DemandeExoneration"
nouveau_import_modeles = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal, DemandeExoneration, PlanPaiement"

if nouveau_import_modeles in contenu:
    print("DEJA FAIT : import PlanPaiement deja present.")
elif ancre_import_modeles in contenu:
    contenu = contenu.replace(ancre_import_modeles, nouveau_import_modeles, 1)
    changements += 1
    print("OK : import PlanPaiement ajoute.")
else:
    print("ERREUR : ligne d'import des modeles introuvable.")

ancre_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm, DemandeExonerationForm"
nouveau_import_forms = "from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm, DemandeExonerationForm, PlanPaiementForm"

if nouveau_import_forms in contenu:
    print("DEJA FAIT : import PlanPaiementForm deja present.")
elif ancre_import_forms in contenu:
    contenu = contenu.replace(ancre_import_forms, nouveau_import_forms, 1)
    changements += 1
    print("OK : import PlanPaiementForm ajoute.")
else:
    print("ERREUR : ligne d'import des formulaires introuvable.")

AJOUT = '''

@login_required
def plan_paiement_liste_view(request):
    """Liste des plans de paiement du citoyen connecte, avec leurs echeances."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    plans = []
    if profil:
        plans = (
            PlanPaiement.objects.filter(contribuable=profil.contribuable)
            .select_related("taxation", "taxation__type_taxe", "taxation__parcelle")
            .prefetch_related("echeances")
            .order_by("-date_soumission")
        )

    return render(request, "citoyens/espace/plan_paiement_liste.html", {
        "plans": plans,
        "citoyen": citoyen,
        "active_section": "plans_paiement",
    })


@login_required
def plan_paiement_creer_view(request, taxation_pk):
    """Depot d'une demande de plan de paiement pour une taxation precise."""
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
        form = PlanPaiementForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.taxation = taxation
            plan.contribuable = profil.contribuable
            plan.save()
            messages.success(request, "Votre demande de plan de paiement a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_plan_paiement_liste")
    else:
        form = PlanPaiementForm()

    return render(request, "citoyens/espace/plan_paiement_form.html", {
        "form": form,
        "taxation": taxation,
        "citoyen": citoyen,
        "active_section": "plans_paiement",
    })


@login_required
def echeance_payer_view(request, echeance_pk):
    """
    Paiement d'une echeance precise d'un plan de paiement valide.
    Reprend exactement le meme mecanisme que payer_taxation_view : le
    paiement reste 'En attente' jusqu'a validation par un agent (voir
    dashboard_paiement_valider, qui met egalement a jour cette echeance
    et le plan une fois confirme).
    """
    from foncier.models import EcheancePlanPaiement
    from foncier.paiement_gateway import initier_paiement

    profil = getattr(request.user, "profil_citoyen", None)
    if profil is None or not profil.actif:
        raise PermissionDenied("Votre compte n'est pas encore relié à un dossier contribuable.")

    echeance = get_object_or_404(
        EcheancePlanPaiement.objects.select_related("plan", "plan__taxation"),
        pk=echeance_pk, plan__contribuable=profil.contribuable,
    )

    if echeance.statut == "PAYEE":
        messages.info(request, "Cette échéance est déjà réglée.")
        return redirect("citoyen_plan_paiement_liste")

    if request.method == "POST":
        form = PaiementEnLigneForm(request.POST)
        if form.is_valid():
            resultat = initier_paiement(
                taxation=echeance.plan.taxation,
                montant=echeance.montant,
                telephone=form.cleaned_data["telephone"],
                request=request,
                backend=form.cleaned_data["operateur"],
            )
            if not resultat["ok"]:
                messages.error(request, resultat["erreur"] or "Le paiement n'a pas pu être initié.")
            else:
                echeance.paiement = resultat["paiement"]
                echeance.save(update_fields=["paiement"])

                if resultat["redirect_url"]:
                    return redirect(resultat["redirect_url"])
                return redirect("citoyen_paiement_retour", pk=resultat["paiement"].pk)
    else:
        initial = {}
        citoyen = getattr(request.user, "citoyen", None)
        if citoyen is not None:
            if citoyen.operateur_paiement:
                initial["operateur"] = citoyen.operateur_paiement
            if citoyen.telephone:
                initial["telephone"] = citoyen.telephone
        form = PaiementEnLigneForm(initial=initial)

    return render(request, "citoyens/espace/echeance_payer.html", {
        "echeance": echeance,
        "form": form,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def plan_paiement_liste_view" in contenu_a_jour:
    print("DEJA FAIT : vues deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : 3 vues plan de paiement ajoutees a la fin du fichier.")

print(f"\n=== {changements} changement(s) enregistres. ===")