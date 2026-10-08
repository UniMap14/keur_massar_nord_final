CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

@login_required
def historique_parcelle_view(request, pk):
    """
    Affiche la chronologie complete d'une parcelle : premiere
    immatriculation, mutations validees (changements de proprietaire),
    et evenements de fusion/morcellement. Reserve au citoyen
    proprietaire (les noms de proprietaires successifs y figurent,
    meme principe de confidentialite que l'extrait cadastral).
    """
    from foncier.models import Parcelle, DemandeImmatriculation, DemandeMutation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    parcelle = get_object_or_404(
        Parcelle.objects.select_related("proprietaire", "demande_origine", "zone"), pk=pk
    )

    parcelles_qs = _parcelles_du_citoyen_qs(request.user)
    if parcelle not in parcelles_qs:
        messages.error(request, "Vous n'avez pas accès à l'historique de cette parcelle.")
        return redirect("citoyen_espace")

    immatriculation = (
        DemandeImmatriculation.objects
        .filter(parcelle=parcelle, statut="VALIDEE")
        .select_related("contribuable_cree")
        .order_by("date_traitement")
        .first()
    )

    mutations = (
        DemandeMutation.objects
        .filter(parcelle=parcelle, statut="VALIDEE")
        .select_related("nouveau_contribuable_cree")
        .order_by("date_traitement")
    )

    demandes_absorbant = (
        parcelle.demandes_morcellement_fusion_origine
        .filter(statut="VALIDEE")
        .prefetch_related("parcelles_resultantes", "parcelles_concernees")
        .order_by("date_traitement")
    )

    return render(request, "citoyens/espace/historique_parcelle.html", {
        "parcelle": parcelle,
        "immatriculation": immatriculation,
        "mutations": mutations,
        "demandes_absorbant": demandes_absorbant,
        "origine": parcelle.demande_origine,
        "citoyen": citoyen,
    })
'''

if "def historique_parcelle_view" in contenu:
    print("DEJA FAIT : vue deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : vue historique_parcelle_view ajoutee.")