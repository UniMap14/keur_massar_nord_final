CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    DemandeMutation,\n)"
nouveau_modele = "    DemandeMutation,\n    DemandeMorcellementFusion,\n)"

if nouveau_modele in contenu:
    print("DEJA FAIT : import DemandeMorcellementFusion deja present.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : DemandeMorcellementFusion ajoute a l'import des modeles.")
else:
    print("ERREUR : ancre 'DemandeMutation,\\n)' introuvable.")

AJOUT = '''

# ============================================================
# MORCELLEMENT / FUSION (cote agent) — examen des demandes de
# division ou de regroupement de parcelles.
# ============================================================

@staff_member_required(login_url='dashboard_login')
def dashboard_morcellement_fusion_list(request):
    """Liste des demandes de morcellement/fusion, filtrable par statut."""
    statut_filtre = request.GET.get("statut", "")
    qs = (
        DemandeMorcellementFusion.objects
        .select_related("demandeur")
        .prefetch_related("parcelles_concernees", "parcelles_resultantes")
        .order_by("-date_soumission")
    )
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)

    return render(request, "dashboard/morcellement_fusion_list.html", {
        "active_section": "morcellement_fusion",
        "demandes": qs,
        "statut_filtre": statut_filtre,
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_morcellement_fusion_traiter(request, pk):
    """
    Examen d'une demande de morcellement/fusion :
    - FUSION : validation = calcule automatiquement l'union des
      geometries (PostGIS), cree la nouvelle parcelle, desactive les
      anciennes.
    - MORCELLEMENT : validation = desactive la parcelle d'origine ;
      l'agent doit ensuite creer manuellement les nouvelles parcelles
      via l'admin Django, en leur assignant cette demande comme
      'demande_origine'.
    """
    from django.contrib.gis.db.models import Union
    import datetime

    demande = get_object_or_404(
        DemandeMorcellementFusion.objects
        .select_related("demandeur")
        .prefetch_related("parcelles_concernees", "parcelles_resultantes"),
        pk=pk,
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "valider":
            parcelles = list(demande.parcelles_concernees.all())

            if demande.type_operation == DemandeMorcellementFusion.TYPE_FUSION:
                resultat = demande.parcelles_concernees.aggregate(geom_union=Union("geom"))
                nouvelle_geom = resultat["geom_union"]

                if nouvelle_geom is None:
                    messages.error(request, "Impossible de calculer l'union des géométries (données manquantes).")
                    return redirect("dashboard_morcellement_fusion_traiter", pk=pk)

                superficie_totale = sum(p.superficie or 0 for p in parcelles)
                premiere = parcelles[0]
                nouveau_nicad = f"FUS-{datetime.date.today().year}-{demande.pk}"

                nouvelle_parcelle = Parcelle.objects.create(
                    nicad=nouveau_nicad,
                    proprietaire=premiere.proprietaire,
                    zone=premiere.zone,
                    superficie=superficie_totale,
                    type_document=premiere.type_document,
                    adresse_parcelle=premiere.adresse_parcelle,
                    occupation_sol=premiere.occupation_sol,
                    geom=nouvelle_geom,
                    demande_origine=demande,
                )

                demande.parcelles_concernees.update(parcelle_active=False)

                messages.success(
                    request,
                    f"Fusion validée — nouvelle parcelle {nouveau_nicad} créée "
                    f"({superficie_totale:.0f} m²), {len(parcelles)} ancienne(s) parcelle(s) désactivée(s)."
                )
            else:
                demande.parcelles_concernees.update(parcelle_active=False)
                messages.success(
                    request,
                    "Morcellement validé — la parcelle d'origine a été désactivée. "
                    "Créez maintenant les nouvelles parcelles via l'admin (en leur assignant "
                    "cette demande comme « Demande d'origine »)."
                )

            demande.statut = DemandeMorcellementFusion.STATUT_VALIDEE
            demande.traite_par = request.user
            demande.date_traitement = timezone.now()
            demande.save()

            return redirect("dashboard_morcellement_fusion_list")

        elif action == "rejeter":
            motif = request.POST.get("motif_rejet", "").strip()
            if not motif:
                messages.error(request, "Merci d'indiquer un motif de rejet.")
            else:
                demande.statut = DemandeMorcellementFusion.STATUT_REJETEE
                demande.motif_rejet = motif
                demande.traite_par = request.user
                demande.date_traitement = timezone.now()
                demande.save()
                messages.info(request, "Demande rejetée.")
                return redirect("dashboard_morcellement_fusion_list")

    return render(request, "dashboard/morcellement_fusion_traiter.html", {
        "active_section": "morcellement_fusion",
        "demande": demande,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_morcellement_fusion_list" in contenu_a_jour:
    print("DEJA FAIT : vues agent deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vues agent morcellement/fusion ajoutees.")

print(f"\n=== {changements} changement(s) enregistres. ===")