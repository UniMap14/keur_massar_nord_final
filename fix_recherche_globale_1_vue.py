# -*- coding: utf-8 -*-
"""
Ajoute dashboard_recherche_globale dans foncier/dashboard_views.py :
recherche intelligente dans parcelles + proprietaires (si acces
cadastre) et contribuables (si acces fiscal), selon le role de
l'agent connecte -- meme cloisonnement que le reste du dashboard.

Idempotent.
"""
import io

chemin = "foncier/dashboard_views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

if "def dashboard_recherche_globale(request):" in contenu:
    print("Deja applique, rien a faire.")
else:
    ancre = "def dashboard_parcelle_list(request):"
    idx = contenu.find(ancre)
    if idx == -1:
        raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")

    idx_ligne = contenu.rfind("\n", 0, idx) + 1
    avant = contenu[:idx_ligne]
    lignes_avant = avant.splitlines(keepends=True)
    # Reculer au-dessus des decorateurs (@staff_member_required, @role_requis(...))
    while lignes_avant and lignes_avant[-1].lstrip().startswith("@"):
        lignes_avant.pop()
    avant = "".join(lignes_avant)
    reste = contenu[idx_ligne:]

    nouveau_bloc = '''@staff_member_required(login_url='dashboard_login')
def dashboard_recherche_globale(request):
    """Recherche intelligente dans tout le dashboard : parcelles et
    proprietaires (service cadastre), contribuables (service fiscal).
    Chaque section n'apparait que si l'agent connecte a le role qui y
    donne acces -- meme cloisonnement que le reste du dashboard."""
    from .permissions import a_role
    from .models import Parcelle, Contribuable, Propri\u00e9taire

    q = request.GET.get("q", "").strip()
    peut_technique = a_role(request.user, "technique")
    peut_fiscal = a_role(request.user, "fiscal")

    parcelles = []
    proprietaires = []
    contribuables = []

    if q:
        if peut_technique:
            parcelles = list(
                Parcelle.objects.select_related("proprietaire", "zone")
                .filter(
                    Q(nicad__icontains=q)
                    | Q(numero_parcelle__icontains=q)
                    | Q(numero_titre_foncier__icontains=q)
                    | Q(adresse_parcelle__icontains=q)
                    | Q(proprietaire__nom__icontains=q)
                    | Q(proprietaire__prenom__icontains=q)
                )
                .order_by("-id")[:20]
            )
            proprietaires = list(
                Propri\u00e9taire.objects.filter(
                    Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(ni_cni__icontains=q)
                ).order_by("nom", "prenom")[:20]
            )

        if peut_fiscal:
            contribuables = list(
                Contribuable.objects.select_related("proprietaire")
                .filter(
                    Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(numero_fiscal__icontains=q)
                ).order_by("nom", "prenom")[:20]
            )

    total = len(parcelles) + len(proprietaires) + len(contribuables)

    context = {
        "active_section": "recherche_globale",
        "q": q,
        "parcelles": parcelles,
        "proprietaires": proprietaires,
        "contribuables": contribuables,
        "total": total,
        "peut_technique": peut_technique,
        "peut_fiscal": peut_fiscal,
        "recherche_effectuee": bool(q),
    }
    return render(request, "dashboard/recherche_globale.html", context)


'''

    nouveau_contenu = avant + nouveau_bloc + reste
    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(nouveau_contenu)
    print("Patch applique avec succes.")
    print("Nouvelle longueur du fichier :", len(nouveau_contenu), "caracteres")