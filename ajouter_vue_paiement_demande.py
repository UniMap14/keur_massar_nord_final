CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

@login_required
def demande_payer_view(request, pk):
    """
    Paiement du tarif d'une demarche payante (extrait cadastral...).
    Reste 'En attente' jusqu'a validation par un agent, comme les
    paiements fiscaux (voir TraitementDemandeForm.statut_paiement).
    """
    import uuid

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    demande = get_object_or_404(DemandeService, pk=pk, demandeur=request.user)

    if not demande.type_demande.tarif or demande.type_demande.tarif <= 0:
        messages.info(request, "Cette démarche est gratuite, aucun paiement n'est nécessaire.")
        return redirect("citoyen_demande_detail", pk=demande.pk)

    if demande.statut_paiement == "CONFIRME":
        messages.info(request, "Cette démarche est déjà payée.")
        return redirect("citoyen_demande_detail", pk=demande.pk)

    if request.method == "POST":
        form = PaiementEnLigneForm(request.POST)
        if form.is_valid():
            demande.montant_paye = demande.type_demande.tarif
            demande.reference_paiement = f"DEMO-{uuid.uuid4().hex[:10].upper()}"
            demande.statut_paiement = "EN_ATTENTE"
            demande.save(update_fields=["montant_paye", "reference_paiement", "statut_paiement"])
            messages.success(request, "Votre paiement a bien été enregistré. Il sera validé par un agent sous peu.")
            return redirect("citoyen_demande_detail", pk=demande.pk)
    else:
        initial = {}
        if citoyen.operateur_paiement:
            initial["operateur"] = citoyen.operateur_paiement
        if citoyen.telephone:
            initial["telephone"] = citoyen.telephone
        form = PaiementEnLigneForm(initial=initial)

    return render(request, "citoyens/demandes/demande_payer.html", {
        "demande": demande,
        "form": form,
        "citoyen": citoyen,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def demande_payer_view" in contenu_a_jour:
    print("DEJA FAIT : vue deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : vue demande_payer_view ajoutee.")