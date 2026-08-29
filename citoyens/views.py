import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.http import JsonResponse, FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from foncier.models import Parcelle, ProfilCitoyen, DemandeService

from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm
from .models import Citoyen


def _envoyer_email_validation(request, citoyen):
    """Envoie un email au citoyen pour l'informer que son compte est validé."""
    login_url = request.build_absolute_uri(reverse("citoyen_login"))
    contexte = {
        "citoyen": citoyen,
        "prenom": citoyen.user.first_name or citoyen.user.username,
        "login_url": login_url,
    }
    corps = render_to_string("citoyens/emails/compte_valide.txt", contexte)
    send_mail(
        subject="Votre espace citoyen KMS Nord est activé",
        message=corps,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[citoyen.user.email],
        fail_silently=False,
    )


def _envoyer_email_rejet(citoyen):
    """Envoie un email au citoyen pour l'informer que son inscription est rejetée."""
    contexte = {
        "citoyen": citoyen,
        "prenom": citoyen.user.first_name or citoyen.user.username,
        "motif": citoyen.motif_rejet or "non précisé",
    }
    corps = render_to_string("citoyens/emails/compte_rejete.txt", contexte)
    send_mail(
        subject="Votre inscription KMS Nord n'a pas été validée",
        message=corps,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[citoyen.user.email],
        fail_silently=False,
    )


def _envoyer_email_demande_recue(request, demande):
    """Confirme au citoyen que sa démarche a bien été enregistrée."""
    suivi_url = request.build_absolute_uri(
        reverse("citoyen_demande_detail", args=[demande.pk])
    )
    contexte = {
        "demande": demande,
        "prenom": demande.demandeur.first_name or demande.demandeur.username,
        "suivi_url": suivi_url,
    }
    corps = render_to_string("citoyens/emails/demande_recue.txt", contexte)
    send_mail(
        subject=f"Demande enregistrée — dossier {demande.numero_dossier}",
        message=corps,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[demande.demandeur.email],
        fail_silently=False,
    )


def _envoyer_email_demande_statut_maj(request, demande):
    """Prévient le citoyen que le statut de sa démarche a changé."""
    suivi_url = request.build_absolute_uri(
        reverse("citoyen_demande_detail", args=[demande.pk])
    )
    contexte = {
        "demande": demande,
        "prenom": demande.demandeur.first_name or demande.demandeur.username,
        "statut_libelle": demande.get_statut_display(),
        "suivi_url": suivi_url,
    }
    corps = render_to_string("citoyens/emails/demande_statut_maj.txt", contexte)
    send_mail(
        subject=f"Mise à jour de votre dossier {demande.numero_dossier} — {demande.get_statut_display()}",
        message=corps,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[demande.demandeur.email],
        fail_silently=False,
    )


class CitoyenRegisterView(CreateView):
    """Formulaire public d'inscription des citoyens."""
    form_class = CitoyenRegistrationForm
    template_name = "citoyens/register.html"
    success_url = reverse_lazy("citoyen_registration_pending")


def registration_pending_view(request):
    """Page affichée juste après l'inscription : 'en attente de validation'."""
    return render(request, "citoyens/registration_pending.html")


class CitoyenLoginView(LoginView):
    """
    Login citoyen. Bloque l'accès à l'espace personnel tant que
    l'administration n'a pas validé le compte (statut Citoyen).
    """
    # Réutilise le même template que la page de connexion de gestion
    # (foncier/templates/dashboard/login.html) : pas de duplication.
    template_name = "dashboard/login.html"
    redirect_authenticated_user = False

    def get_default_redirect_url(self):
        # Ignore LOGIN_REDIRECT_URL (qui pointe vers /gestion/ pour les agents) :
        # un citoyen doit atterrir sur son espace personnel, sauf si un
        # paramètre '?next=' précis a été fourni (géré par la classe parente).
        return reverse("citoyen_espace")

    def form_valid(self, form):
        user = form.get_user()
        citoyen = getattr(user, "citoyen", None)

        if citoyen is not None and not citoyen.est_valide:
            if citoyen.est_en_attente:
                message = (
                    "Votre inscription est en attente de validation par l'administration. "
                    "Vous recevrez un accès dès que votre dossier aura été vérifié."
                )
            else:
                motif = citoyen.motif_rejet or "non précisé"
                message = f"Votre inscription a été refusée. Motif : {motif}"
            form.add_error(None, message)
            return self.form_invalid(form)

        return super().form_valid(form)


@login_required
def espace_personnel_view(request):
    """
    Espace personnel du citoyen connecté (fiscalité / foncier).

    Les données réelles de taxation (montants dus, paiements, parcelles)
    sont accessibles quand le compte a été relié à un Contribuable via un
    ProfilCitoyen (foncier.ProfilCitoyen). Tant que l'administration n'a
    pas fait ce lien, on affiche uniquement les identifiants saisis à
    l'inscription et une invitation à contacter la mairie.
    """
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        # L'utilisateur connecté n'est pas un citoyen (ex: agent staff) :
        # pas d'espace personnel citoyen pour lui.
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    contribuable = None
    taxations = []
    nicads_lies = []
    profil = getattr(request.user, "profil_citoyen", None)
    if profil is not None and profil.actif:
        contribuable = profil.contribuable
        taxations = (
            contribuable.taxations
            .select_related("type_taxe", "parcelle")
            .prefetch_related("paiements")
            .order_by("-annee_fiscale", "type_taxe__libelle")
        )
        nicads_lies = list(
            taxations.exclude(parcelle__isnull=True)
            .values_list("parcelle__nicad", flat=True)
            .distinct()
        )

    return render(request, "citoyens/espace/espace_personnel.html", {
        "citoyen": citoyen,
        "contribuable": contribuable,
        "taxations": taxations,
        "nicads_lies": nicads_lies,
    })


@login_required
def payer_taxation_view(request, pk):
    """
    Paiement en ligne d'une taxation par le citoyen connecté.

    Vérification de sécurité essentielle : la taxation demandée doit
    appartenir au contribuable lié au compte connecté — jamais à celui
    d'un autre citoyen, même en devinant un autre numéro dans l'URL.
    """
    from foncier.models import Taxation
    from foncier.paiement_gateway import initier_paiement

    profil = getattr(request.user, "profil_citoyen", None)
    if profil is None or not profil.actif:
        raise PermissionDenied("Votre compte n'est pas encore relié à un dossier contribuable.")

    taxation = get_object_or_404(Taxation, pk=pk, contribuable=profil.contribuable)

    if taxation.solde <= 0:
        messages.info(request, "Cette taxation est déjà réglée.")
        return redirect("citoyen_espace")

    if request.method == "POST":
        form = PaiementEnLigneForm(request.POST)
        if form.is_valid():
            resultat = initier_paiement(
                taxation=taxation,
                montant=taxation.solde,
                telephone=form.cleaned_data["telephone"],
                request=request,
                backend=form.cleaned_data["operateur"],
            )
            if not resultat["ok"]:
                messages.error(request, resultat["erreur"] or "Le paiement n'a pas pu être initié.")
            elif resultat["redirect_url"]:
                # Redirection vers la page de paiement hébergée par l'opérateur.
                return redirect(resultat["redirect_url"])
            else:
                # Backend "manuel" (démonstration) : déjà confirmé.
                return redirect("citoyen_paiement_retour", pk=resultat["paiement"].pk)
    else:
        form = PaiementEnLigneForm()

    return render(request, "citoyens/espace/payer_taxation.html", {
        "taxation": taxation,
        "form": form,
    })


@login_required
def paiement_retour_view(request, pk):
    """Page sur laquelle le citoyen revient après un paiement en ligne
    (ou juste après un paiement 'manuel' de démonstration) : affiche le
    statut actuel du paiement. Le webhook de l'opérateur peut confirmer
    le paiement séparément, un peu avant ou après cet affichage."""
    from foncier.models import Paiement

    profil = getattr(request.user, "profil_citoyen", None)
    paiement = get_object_or_404(
        Paiement.objects.select_related("taxation", "taxation__contribuable"),
        pk=pk,
    )

    # Même vérification de propriété que pour l'initiation du paiement.
    if profil is None or paiement.taxation.contribuable_id != profil.contribuable_id:
        raise PermissionDenied("Ce paiement n'appartient pas à votre dossier.")

    return render(request, "citoyens/espace/paiement_retour.html", {
        "paiement": paiement,
    })


@login_required
@login_required
def parcelles_geojson_view(request):
    """
    Renvoie UNIQUEMENT les parcelles du citoyen connecté (via son
    ProfilCitoyen -> Contribuable -> Taxations).

    IMPORTANT (confidentialité) : tant que le compte n'est pas relié à un
    contribuable par l'administration, on ne renvoie AUCUNE parcelle — en
    particulier on ne doit jamais retomber sur "toutes les parcelles",
    car cela exposerait le statut fiscal de tous les habitants de la
    commune à n'importe quel citoyen connecté. Chacun ne doit voir que
    ses propres informations, jamais celles des autres.
    """
    profil = getattr(request.user, "profil_citoyen", None)
    parcelles_du_citoyen = False
    ids_parcelles = []

    if profil is not None and profil.actif:
        ids_parcelles = list(
            profil.contribuable.taxations
            .exclude(parcelle__isnull=True)
            .values_list("parcelle_id", flat=True)
            .distinct()
        )
        parcelles_du_citoyen = bool(ids_parcelles)

    features = []
    if ids_parcelles:
        qs = Parcelle.objects.filter(id__in=ids_parcelles).exclude(geom__isnull=True).only(
            "id", "nicad", "statut_fiscal", "superficie", "occupation_sol", "geom"
        )
        for parcelle in qs.iterator():
            features.append({
                "type": "Feature",
                "geometry": json.loads(parcelle.geom.geojson),
                "properties": {
                    "id": parcelle.id,
                    "nicad": parcelle.nicad,
                    "statut_fiscal": parcelle.statut_fiscal,
                    "superficie": parcelle.superficie,
                    "occupation_sol": parcelle.occupation_sol,
                },
            })
    return JsonResponse({
        "type": "FeatureCollection",
        "features": features,
        "parcelles_du_citoyen": parcelles_du_citoyen,
    })


def _est_agent(user):
    return user.is_staff


@login_required
@user_passes_test(_est_agent)
def gestion_inscriptions_view(request):
    """Page de gestion (dashboard admin) pour valider/rejeter les inscriptions."""
    if request.method == "POST":
        citoyen_id = request.POST.get("citoyen_id")
        action = request.POST.get("action")
        citoyen = get_object_or_404(Citoyen, pk=citoyen_id)

        if action == "valider":
            citoyen.statut = Citoyen.STATUT_VALIDE
            citoyen.date_validation = timezone.now()
            citoyen.valide_par = request.user
            citoyen.motif_rejet = ""
            citoyen.save()
            try:
                _envoyer_email_validation(request, citoyen)
                messages.success(
                    request,
                    f"Inscription de {citoyen.user.get_full_name() or citoyen.user.username} validée. "
                    f"Un email de confirmation a été envoyé à {citoyen.user.email}."
                )
            except Exception:
                messages.warning(
                    request,
                    f"Inscription validée, mais l'email de confirmation n'a pas pu être envoyé "
                    f"à {citoyen.user.email}. Vérifie la configuration email (EMAIL_BACKEND)."
                )
        elif action == "rejeter":
            citoyen.statut = Citoyen.STATUT_REJETE
            citoyen.motif_rejet = request.POST.get("motif", "").strip()
            citoyen.valide_par = request.user
            citoyen.date_validation = timezone.now()
            citoyen.save()
            try:
                _envoyer_email_rejet(citoyen)
                messages.success(
                    request,
                    f"Inscription de {citoyen.user.get_full_name() or citoyen.user.username} rejetée. "
                    f"Un email a été envoyé à {citoyen.user.email}."
                )
            except Exception:
                messages.warning(
                    request,
                    f"Inscription rejetée, mais l'email n'a pas pu être envoyé à {citoyen.user.email}."
                )
        return redirect("gestion_inscriptions")

    citoyens_en_attente = (
        Citoyen.objects.filter(statut=Citoyen.STATUT_EN_ATTENTE)
        .select_related("user")
        .order_by("date_inscription")
    )
    citoyens_traites = (
        Citoyen.objects.exclude(statut=Citoyen.STATUT_EN_ATTENTE)
        .select_related("user")
        .order_by("-date_validation")[:50]
    )
    return render(request, "citoyens/gestion_inscriptions.html", {
        "active_section": "inscriptions",
        "citoyens_en_attente": citoyens_en_attente,
        "citoyens_traites": citoyens_traites,
    })

def _parcelles_du_citoyen_qs(user):
    """Renvoie les parcelles associées au dossier fiscal du citoyen connecté (ou queryset vide)."""
    profil = getattr(user, "profil_citoyen", None)
    if profil is None or not profil.actif:
        return Parcelle.objects.none()
    ids = (
        profil.contribuable.taxations
        .exclude(parcelle__isnull=True)
        .values_list("parcelle_id", flat=True)
        .distinct()
    )
    return Parcelle.objects.filter(id__in=ids)


@login_required
def demandes_liste_view(request):
    """Liste des démarches déposées par le citoyen connecté, avec leur statut."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    demandes = (
        DemandeService.objects
        .filter(demandeur=request.user)
        .select_related("type_demande", "parcelle")
        .order_by("-date_demande")
    )
    return render(request, "citoyens/demandes/demandes_liste.html", {
        "citoyen": citoyen,
        "demandes": demandes,
    })


@login_required
def _envoyer_email_notif_agents_demande(request, demande):
    """Notification interne à l'administration qu'une nouvelle démarche
    citoyenne vient d'être déposée. Best-effort (n'empêche jamais le
    reste du parcours citoyen de continuer en cas d'échec)."""
    lien_dashboard = request.build_absolute_uri(
        reverse('dashboard_demande_detail', args=[demande.pk])
    )
    send_mail(
        subject=f"[KMS Nord] Nouvelle démarche : {demande.type_demande.libelle} — {demande.numero_dossier}",
        message=(
            f"Une nouvelle démarche citoyenne a été déposée.\n\n"
            f"Dossier : {demande.numero_dossier}\n"
            f"Type : {demande.type_demande.libelle}\n"
            f"Citoyen : {demande.demandeur.get_full_name() or demande.demandeur.username}\n"
            f"Date : {demande.date_demande:%d/%m/%Y %H:%M}\n\n"
            f"Voir et traiter cette démarche :\n{lien_dashboard}"
        ),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=settings.NOTIF_AGENTS_EMAIL,
        fail_silently=True,
    )


def demande_creer_view(request):
    """Formulaire de dépôt d'une nouvelle démarche en ligne."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    parcelles_qs = _parcelles_du_citoyen_qs(request.user)

    if request.method == "POST":
        form = DemandeServiceForm(request.POST, request.FILES, parcelles_qs=parcelles_qs)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            try:
                _envoyer_email_demande_recue(request, demande)
            except Exception:
                messages.warning(
                    request,
                    "Votre demande a été enregistrée, mais l'email de confirmation n'a pas pu être envoyé."
                )
            try:
                _envoyer_email_notif_agents_demande(request, demande)
            except Exception:
                pass
            messages.success(
                request,
                f"Votre demande a bien été enregistrée sous le numéro {demande.numero_dossier}. "
                f"Vous pouvez suivre son avancement depuis « Mes démarches »."
            )
            return redirect("citoyen_demandes")
    else:
        form = DemandeServiceForm(parcelles_qs=parcelles_qs)

    return render(request, "citoyens/demandes/demande_form.html", {
        "citoyen": citoyen,
        "form": form,
    })


@login_required
def demande_detail_view(request, pk):
    """Suivi détaillé d'une démarche (réservé à son auteur)."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    demande = get_object_or_404(
        DemandeService.objects.select_related("type_demande", "parcelle"),
        pk=pk, demandeur=request.user,
    )
    return render(request, "citoyens/demandes/demande_detail.html", {
        "citoyen": citoyen,
        "demande": demande,
    })


@login_required
def demande_piece_jointe_view(request, pk):
    """
    Sert la pièce jointe d'une démarche, uniquement à son auteur ou à un
    agent (is_staff). Le fichier est stocké hors de MEDIA_ROOT (voir
    foncier.models.stockage_pieces_jointes) : c'est la SEULE façon d'y
    accéder, il n'existe aucune URL /media/... publique pour ces documents.
    """
    demande = get_object_or_404(DemandeService, pk=pk)

    if demande.demandeur_id != request.user.id and not request.user.is_staff:
        raise PermissionDenied("Vous n'avez pas accès à ce document.")

    if not demande.piece_jointe:
        raise Http404("Cette demande n'a pas de pièce jointe.")

    nom_fichier = demande.piece_jointe.name.split("/")[-1]
    return FileResponse(
        demande.piece_jointe.open("rb"),
        as_attachment=True,
        filename=nom_fichier,
    )


@login_required
def modifier_profil_view(request):
    """Permet au citoyen connecté de modifier ses informations personnelles."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    if request.method == "POST":
        form = ModifierProfilForm(request.POST, user=request.user, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "telephone": citoyen.telephone,
        })
        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()

            citoyen.telephone = form.cleaned_data["telephone"]
            citoyen.save()

            messages.success(request, "Vos informations ont été mises à jour.")
            return redirect("citoyen_espace")
    else:
        form = ModifierProfilForm(user=request.user, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "telephone": citoyen.telephone,
        })

    return render(request, "citoyens/espace/modifier_profil.html", {
        "citoyen": citoyen,
        "form": form,
    })