CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    EcheancePlanPaiement,\n)"
nouveau_modele = "    EcheancePlanPaiement,\n    DemandeMutation,\n)"

if nouveau_modele in contenu:
    print("DEJA FAIT : import DemandeMutation deja present.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : DemandeMutation ajoute a l'import des modeles.")
else:
    print("ERREUR : ancre 'EcheancePlanPaiement,\\n)' introuvable.")

AJOUT = '''

# ============================================================
# MUTATIONS FISCALES (cote agent) — examen des demandes de transfert
# de dossier fiscal suite a une revente.
# ============================================================

@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_mutation_list(request):
    """Liste des demandes de mutation fiscale, filtrable par statut."""
    statut_filtre = request.GET.get("statut", "")
    qs = (
        DemandeMutation.objects
        .select_related("parcelle", "parcelle__proprietaire")
        .order_by("-date_soumission")
    )
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)

    return render(request, "dashboard/mutation_list.html", {
        "active_section": "mutations",
        "demandes": qs,
        "statut_filtre": statut_filtre,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_mutation_traiter(request, pk):
    """
    Examen d'une demande de mutation : validation (cree le nouveau
    proprietaire/contribuable, rattache la parcelle, notifie par
    email) ou rejet (avec motif).
    """
    demande = get_object_or_404(
        DemandeMutation.objects.select_related("parcelle", "parcelle__proprietaire"), pk=pk
    )

    ancien_contribuable = None
    if demande.parcelle.proprietaire_id:
        ancien_contribuable = Contribuable.objects.filter(
            proprietaire_id=demande.parcelle.proprietaire_id
        ).first()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "valider":
            nouveau_proprietaire, _ = Propriétaire.objects.get_or_create(
                ni_cni=demande.nouveau_cni,
                defaults={
                    "nom": demande.nouveau_nom,
                    "prenom": demande.nouveau_prenom,
                    "telephone": demande.nouveau_telephone,
                },
            )

            demande.parcelle.proprietaire = nouveau_proprietaire
            demande.parcelle.save(update_fields=["proprietaire"])

            numero_fiscal = _generer_numero_fiscal()
            nouveau_contribuable = Contribuable.objects.create(
                proprietaire=nouveau_proprietaire,
                numero_fiscal=numero_fiscal,
                nom=demande.nouveau_nom,
                prenom=demande.nouveau_prenom,
                telephone=demande.nouveau_telephone,
            )

            demande.statut = DemandeMutation.STATUT_VALIDEE
            demande.nouveau_contribuable_cree = nouveau_contribuable
            demande.traite_par = request.user
            demande.date_traitement = timezone.now()
            demande.save()

            if demande.nouveau_email:
                try:
                    send_mail(
                        subject="[KEUR MASSAR NORD] Votre mutation fiscale",
                        message=(
                            f"Bonjour {demande.nouveau_prenom},\\n\\n"
                            f"Votre demande de mutation fiscale a été validée.\\n"
                            f"Votre numéro fiscal est : {numero_fiscal}\\n"
                            f"Votre numéro foncier (NICAD) est : {demande.parcelle.nicad}\\n\\n"
                            f"Vous pouvez désormais créer votre compte dans l'espace citoyen "
                            f"en utilisant ces deux identifiants."
                        ),
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=[demande.nouveau_email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            messages.success(request, f"Mutation validée — numéro fiscal {numero_fiscal} attribué au nouveau propriétaire.")
            return redirect("dashboard_mutation_list")

        elif action == "rejeter":
            motif = request.POST.get("motif_rejet", "").strip()
            if not motif:
                messages.error(request, "Merci d'indiquer un motif de rejet.")
            else:
                demande.statut = DemandeMutation.STATUT_REJETEE
                demande.motif_rejet = motif
                demande.traite_par = request.user
                demande.date_traitement = timezone.now()
                demande.save()
                messages.info(request, "Demande rejetée.")
                return redirect("dashboard_mutation_list")

    return render(request, "dashboard/mutation_traiter.html", {
        "active_section": "mutations",
        "demande": demande,
        "ancien_contribuable": ancien_contribuable,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_mutation_list" in contenu_a_jour:
    print("DEJA FAIT : vues agent deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vues agent mutation ajoutees.")

print(f"\n=== {changements} changement(s) enregistres. ===")