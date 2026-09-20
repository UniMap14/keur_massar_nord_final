CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    DemandeExoneration,\n)"
nouveau_modele = "    DemandeExoneration,\n    PlanPaiement,\n    EcheancePlanPaiement,\n)"

if nouveau_modele in contenu:
    print("DEJA FAIT : import PlanPaiement deja present.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : PlanPaiement + EcheancePlanPaiement ajoutes a l'import des modeles.")
else:
    print("ERREUR : ancre 'DemandeExoneration,\\n)' introuvable.")

AJOUT = '''

# ============================================================
# PLANS DE PAIEMENT (cote agent) — examen des demandes
# d'echelonnement, generation automatique des echeances a la
# validation.
# ============================================================

@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_plan_paiement_list(request):
    """Liste des demandes de plan de paiement, filtrable par statut."""
    statut_filtre = request.GET.get("statut", "")
    qs = (
        PlanPaiement.objects
        .select_related("contribuable", "taxation", "taxation__type_taxe", "taxation__parcelle")
        .order_by("-date_soumission")
    )
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)

    return render(request, "dashboard/plan_paiement_list.html", {
        "active_section": "plans_paiement",
        "plans": qs,
        "statut_filtre": statut_filtre,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_plan_paiement_traiter(request, pk):
    """Examen d'une demande de plan de paiement : validation (genere
    les echeances, montants egaux, une par mois) ou rejet (avec motif)."""
    import datetime
    from decimal import ROUND_HALF_UP

    plan = get_object_or_404(
        PlanPaiement.objects.select_related("contribuable", "taxation"), pk=pk
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "valider":
            solde = plan.taxation.solde
            n = plan.nombre_echeances
            montant_par_echeance = (solde / n).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

            aujourdhui = datetime.date.today()
            total_reparti = Decimal("0")
            for i in range(1, n + 1):
                mois_a_ajouter = i
                annee = aujourdhui.year + (aujourdhui.month - 1 + mois_a_ajouter) // 12
                mois = (aujourdhui.month - 1 + mois_a_ajouter) % 12 + 1
                date_prevue = datetime.date(annee, mois, min(aujourdhui.day, 28))

                montant_echeance = montant_par_echeance
                if i == n:
                    montant_echeance = solde - total_reparti
                total_reparti += montant_echeance

                EcheancePlanPaiement.objects.create(
                    plan=plan,
                    numero=i,
                    montant=montant_echeance,
                    date_prevue=date_prevue,
                )

            plan.statut = PlanPaiement.STATUT_VALIDE
            plan.traite_par = request.user
            plan.date_traitement = timezone.now()
            plan.save()

            messages.success(request, f"Plan de paiement validé — {n} échéance(s) générée(s).")
            return redirect("dashboard_plan_paiement_list")

        elif action == "rejeter":
            motif = request.POST.get("motif_rejet", "").strip()
            if not motif:
                messages.error(request, "Merci d'indiquer un motif de rejet.")
            else:
                plan.statut = PlanPaiement.STATUT_REJETE
                plan.motif_rejet = motif
                plan.traite_par = request.user
                plan.date_traitement = timezone.now()
                plan.save()
                messages.info(request, "Demande rejetée.")
                return redirect("dashboard_plan_paiement_list")

    return render(request, "dashboard/plan_paiement_traiter.html", {
        "active_section": "plans_paiement",
        "plan": plan,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_plan_paiement_list" in contenu_a_jour:
    print("DEJA FAIT : vues agent deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vues agent plan de paiement ajoutees.")

print(f"\n=== {changements} changement(s) enregistres. ===")