CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    DeclarationFiscale,\n)"
nouveau_modele = "    DeclarationFiscale,\n    RecoursFiscal,\n)"

if nouveau_modele in contenu:
    print("DEJA FAIT : import RecoursFiscal deja present.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : RecoursFiscal ajoute a l'import des modeles.")
else:
    print("ERREUR : ancre 'DeclarationFiscale,\\n)' introuvable.")

AJOUT = '''

# ============================================================
# RECOURS FISCAUX (cote agent) — examen des contestations de taxation
# et des demandes de redressement deposees par les citoyens.
# ============================================================

@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_recours_list(request):
    """Liste des recours/redressements fiscaux, filtrable par statut."""
    statut_filtre = request.GET.get("statut", "")
    qs = (
        RecoursFiscal.objects
        .select_related("contribuable", "taxation", "taxation__type_taxe", "taxation__parcelle")
        .order_by("-date_soumission")
    )
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)

    return render(request, "dashboard/recours_list.html", {
        "active_section": "recours",
        "recours_liste": qs,
        "statut_filtre": statut_filtre,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_recours_traiter(request, pk):
    """Examen d'un recours/redressement : acceptation (corrige le
    montant de la taxation) ou rejet (avec explication)."""
    recours = get_object_or_404(
        RecoursFiscal.objects.select_related(
            "contribuable", "taxation", "taxation__type_taxe", "taxation__parcelle", "recours_precedent"
        ),
        pk=pk,
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accepter":
            nouveau_montant_str = request.POST.get("nouveau_montant", "").strip()
            try:
                nouveau_montant = Decimal(nouveau_montant_str)
            except Exception:
                messages.error(request, "Montant invalide.")
                return redirect("dashboard_recours_traiter", pk=pk)

            recours.ancien_montant = recours.taxation.montant_du
            recours.nouveau_montant = nouveau_montant
            recours.taxation.montant_du = nouveau_montant
            recours.taxation.save(update_fields=["montant_du"])

            recours.statut = RecoursFiscal.STATUT_ACCEPTE
            recours.traite_par = request.user
            recours.date_traitement = timezone.now()
            recours.decision_commentaire = request.POST.get("decision_commentaire", "").strip()
            recours.save()

            messages.success(request, f"Recours accepté — nouveau montant : {nouveau_montant:,.0f} FCFA.".replace(",", " "))
            return redirect("dashboard_recours_list")

        elif action == "rejeter":
            commentaire = request.POST.get("decision_commentaire", "").strip()
            if not commentaire:
                messages.error(request, "Merci d'indiquer une explication pour le rejet.")
            else:
                recours.statut = RecoursFiscal.STATUT_REJETE
                recours.traite_par = request.user
                recours.date_traitement = timezone.now()
                recours.decision_commentaire = commentaire
                recours.save()
                messages.info(request, "Recours rejeté.")
                return redirect("dashboard_recours_list")

    return render(request, "dashboard/recours_traiter.html", {
        "active_section": "recours",
        "recours": recours,
    })
'''

if "from decimal import Decimal" not in contenu:
    contenu = contenu.replace(
        "from django.conf import settings",
        "from django.conf import settings\nfrom decimal import Decimal",
        1,
    )
    changements += 1
    print("OK : import Decimal ajoute.")
else:
    print("DEJA FAIT : import Decimal deja present.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_recours_list" in contenu_a_jour:
    print("DEJA FAIT : vues recours agent deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : 2 vues agent (recours) ajoutees a la fin du fichier.")

print(f"\n=== {changements} changement(s) enregistres. ===")