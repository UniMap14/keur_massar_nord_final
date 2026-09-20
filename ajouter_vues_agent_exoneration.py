CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    DemandeImmatriculation,\n)"
nouveau_modele = "    DemandeImmatriculation,\n    DemandeExoneration,\n)"

if nouveau_modele in contenu:
    print("DEJA FAIT : import DemandeExoneration deja present.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : DemandeExoneration ajoute a l'import des modeles.")
else:
    print("ERREUR : ancre 'DemandeImmatriculation,\\n)' introuvable.")

AJOUT = '''

# ============================================================
# EXONERATIONS FISCALES (cote agent) — examen des demandes citoyennes.
# ============================================================

@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_exoneration_list(request):
    """Liste des demandes d'exoneration fiscale, filtrable par statut."""
    statut_filtre = request.GET.get("statut", "")
    qs = (
        DemandeExoneration.objects
        .select_related("contribuable", "parcelle")
        .order_by("-date_soumission")
    )
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)

    return render(request, "dashboard/exoneration_list.html", {
        "active_section": "exonerations",
        "demandes": qs,
        "statut_filtre": statut_filtre,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_exoneration_traiter(request, pk):
    """Examen d'une demande d'exoneration : validation (passe la
    parcelle au statut fiscal EXONERE) ou rejet (avec motif)."""
    demande = get_object_or_404(
        DemandeExoneration.objects.select_related("contribuable", "parcelle"), pk=pk
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "valider":
            demande.parcelle.statut_fiscal = "EXONERE"
            demande.parcelle.save(update_fields=["statut_fiscal"])

            demande.statut = DemandeExoneration.STATUT_VALIDEE
            demande.traite_par = request.user
            demande.date_traitement = timezone.now()
            demande.save()

            messages.success(request, f"Exonération validée — la parcelle {demande.parcelle.nicad} est désormais exonérée.")
            return redirect("dashboard_exoneration_list")

        elif action == "rejeter":
            motif = request.POST.get("motif_rejet", "").strip()
            if not motif:
                messages.error(request, "Merci d'indiquer un motif de rejet.")
            else:
                demande.statut = DemandeExoneration.STATUT_REJETEE
                demande.motif_rejet = motif
                demande.traite_par = request.user
                demande.date_traitement = timezone.now()
                demande.save()
                messages.info(request, "Demande rejetée.")
                return redirect("dashboard_exoneration_list")

    return render(request, "dashboard/exoneration_traiter.html", {
        "active_section": "exonerations",
        "demande": demande,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_exoneration_list" in contenu_a_jour:
    print("DEJA FAIT : vues agent deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vues agent exoneration ajoutees.")

print(f"\n=== {changements} changement(s) enregistres. ===")