from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.paginator import Paginator

from foncier.models import Paiement


def connexion(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("dashboard")

        messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "comptes/connexion.html")


@login_required(login_url="connexion")


@login_required(login_url="connexion")
def dashboard(request):

    profil = getattr(request.user, "profil_citoyen", None)
    contribuable = None
    taxations = []
    paiements_page = None

    if profil is None:
        messages.warning(
            request,
            "Aucun profil citoyen n'est associé à ce compte. "
            "Contactez l'administration pour lier votre dossier."
        )
    else:
        contribuable = profil.contribuable

        taxations = (
            contribuable.taxations
            .select_related("type_taxe", "parcelle")
            .order_by("-annee_fiscale")
        )

        paiements = (
            Paiement.objects.filter(taxation__contribuable=contribuable)
            .select_related("taxation", "taxation__type_taxe")
            .order_by("-date_paiement")
        )

        paginator = Paginator(paiements, 10)
        page_number = request.GET.get("page")
        paiements_page = paginator.get_page(page_number)

    return render(
        request,
        "comptes/dashboard.html",
        {
            "profil": profil,
            "contribuable": contribuable,
            "taxations": taxations,
            "paiements": paiements_page,
        }
    )
def deconnexion(request):
    logout(request)
    return redirect("home")