CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    RecoursFiscal,\n)"
nouveau_modele = "    RecoursFiscal,\n    DemandeImmatriculation,\n)"

if nouveau_modele in contenu:
    print("DEJA FAIT : import DemandeImmatriculation deja present.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : DemandeImmatriculation ajoute a l'import des modeles.")
else:
    print("ERREUR : ancre 'RecoursFiscal,\\n)' introuvable.")

AJOUT = '''

# ============================================================
# PREMIERE IMMATRICULATION FISCALE (cote agent) — examen des demandes
# publiques deposees par des personnes qui n'ont jamais ete
# contribuables (voir foncier/views.py:immatriculation_demande_view
# pour le depot public).
# ============================================================

def _generer_numero_fiscal():
    """Genere un numero fiscal KMN-XXXXXX sequentiel et unique, pour
    distinguer les vraies immatriculations des comptes simules
    (prefixe SIMU-)."""
    dernier = (
        Contribuable.objects
        .filter(numero_fiscal__startswith="KMN-")
        .order_by("-numero_fiscal")
        .first()
    )
    if dernier:
        try:
            dernier_num = int(dernier.numero_fiscal.split("-")[1])
        except (IndexError, ValueError):
            dernier_num = 0
    else:
        dernier_num = 0
    return f"KMN-{dernier_num + 1:06d}"


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_immatriculation_list(request):
    """Liste des demandes de premiere immatriculation fiscale, filtrable par statut."""
    statut_filtre = request.GET.get("statut", "")
    qs = (
        DemandeImmatriculation.objects
        .select_related("parcelle")
        .order_by("-date_soumission")
    )
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)

    return render(request, "dashboard/immatriculation_list.html", {
        "active_section": "immatriculations",
        "demandes": qs,
        "statut_filtre": statut_filtre,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_immatriculation_traiter(request, pk):
    """Examen d'une demande d'immatriculation : validation (cree le
    proprietaire, rattache la parcelle, cree le contribuable avec un
    nouveau numero fiscal, notifie par email) ou rejet (avec motif)."""
    demande = get_object_or_404(
        DemandeImmatriculation.objects.select_related("parcelle"), pk=pk
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "valider":
            proprietaire, _ = Propriétaire.objects.get_or_create(
                ni_cni=demande.ni_cni,
                defaults={
                    "nom": demande.nom,
                    "prenom": demande.prenom,
                    "telephone": demande.telephone,
                },
            )

            demande.parcelle.proprietaire = proprietaire
            demande.parcelle.occupation_sol = demande.occupation_declaree
            demande.parcelle.save(update_fields=["proprietaire", "occupation_sol"])

            numero_fiscal = _generer_numero_fiscal()
            contribuable = Contribuable.objects.create(
                proprietaire=proprietaire,
                numero_fiscal=numero_fiscal,
                nom=demande.nom,
                prenom=demande.prenom,
                telephone=demande.telephone,
            )

            demande.statut = DemandeImmatriculation.STATUT_VALIDEE
            demande.contribuable_cree = contribuable
            demande.traite_par = request.user
            demande.date_traitement = timezone.now()
            demande.save()

            if demande.email:
                try:
                    send_mail(
                        subject="[KEUR MASSAR NORD] Votre immatriculation fiscale",
                        message=(
                            f"Bonjour {demande.prenom},\\n\\n"
                            f"Votre demande d'immatriculation fiscale a été validée.\\n"
                            f"Votre numéro fiscal est : {numero_fiscal}\\n"
                            f"Votre numéro foncier (NICAD) est : {demande.parcelle.nicad}\\n\\n"
                            f"Vous pouvez désormais créer votre compte dans l'espace citoyen "
                            f"en utilisant ces deux identifiants."
                        ),
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=[demande.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            messages.success(request, f"Immatriculation validée — numéro fiscal {numero_fiscal} attribué.")
            return redirect("dashboard_immatriculation_list")

        elif action == "rejeter":
            motif = request.POST.get("motif_rejet", "").strip()
            if not motif:
                messages.error(request, "Merci d'indiquer un motif de rejet.")
            else:
                demande.statut = DemandeImmatriculation.STATUT_REJETEE
                demande.motif_rejet = motif
                demande.traite_par = request.user
                demande.date_traitement = timezone.now()
                demande.save()
                messages.info(request, "Demande rejetée.")
                return redirect("dashboard_immatriculation_list")

    return render(request, "dashboard/immatriculation_traiter.html", {
        "active_section": "immatriculations",
        "demande": demande,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_immatriculation_list" in contenu_a_jour:
    print("DEJA FAIT : vues agent deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vues agent immatriculation ajoutees.")

print(f"\n=== {changements} changement(s) enregistres. ===")