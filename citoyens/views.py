import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse, FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale, RecoursFiscal, DemandeExoneration, PlanPaiement, DemandeMorcellementFusion

from .forms import CitoyenRegistrationForm, DemandeServiceForm, ModifierProfilForm, PaiementEnLigneForm, DeclarationFiscaleForm, RecoursFiscalForm, DemandeExonerationForm, PlanPaiementForm, DemandeMorcellementFusionForm
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



class EmailAuthenticationForm(AuthenticationForm):
    """
    Le champ visible dit "Email" (voir dashboard/login.html), mais
    AuthenticationForm attend un nom d'utilisateur : on traduit ici
    l'email saisi vers le vrai username avant que Django ne verifie
    le mot de passe.
    """
    def clean_username(self):
        saisi = self.cleaned_data.get('username', '')
        try:
            user = User.objects.get(email__iexact=saisi)
            return user.username
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return saisi

class CitoyenLoginView(LoginView):
    """
    Login citoyen. Bloque l'accès à l'espace personnel tant que
    l'administration n'a pas validé le compte (statut Citoyen).
    """
    # Réutilise le même template que la page de connexion de gestion
    # (foncier/templates/dashboard/login.html) : pas de duplication.
    template_name = "dashboard/login.html"
    form_class = EmailAuthenticationForm
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

        # Ne connecte pas encore : genere un code a usage unique (OTP)
        # envoye par SMS/email, et redirige vers sa verification -- la
        # connexion Django elle-meme n'a lieu qu'une fois le bon code
        # saisi (voir otp_verify_view).
        import time
        code = _generer_otp()
        self.request.session["otp_user_id"] = user.pk
        self.request.session["otp_code"] = code
        self.request.session["otp_expire"] = time.time() + 300
        self.request.session["otp_next"] = self.get_success_url()
        _envoyer_otp(user, code)

        return redirect("citoyen_otp_verify")


@login_required(login_url='citoyen_login')
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
        # Pre-remplit avec le compte de paiement enregistre dans le
        # profil du citoyen, s'il en a un (moins de friction que de
        # retaper operateur + numero a chaque paiement).
        initial = {}
        citoyen = getattr(request.user, "citoyen", None)
        if citoyen is not None:
            if citoyen.operateur_paiement:
                initial["operateur"] = citoyen.operateur_paiement
            if citoyen.telephone:
                initial["telephone"] = citoyen.telephone
        form = PaiementEnLigneForm(initial=initial)

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
            if demande.type_demande.tarif and demande.type_demande.tarif > 0:
                demande.statut_paiement = "EN_ATTENTE"
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

            if demande.type_demande.tarif and demande.type_demande.tarif > 0:
                messages.success(
                    request,
                    f"Votre demande a bien été enregistrée sous le numéro {demande.numero_dossier}. "
                    f"Cette démarche est payante ({demande.type_demande.tarif:.0f} FCFA) — réglez-la pour lancer son traitement."
                )
                return redirect("citoyen_demande_payer", pk=demande.pk)

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
            "operateur_paiement": citoyen.operateur_paiement,
        })
        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()

            citoyen.telephone = form.cleaned_data["telephone"]
            citoyen.operateur_paiement = form.cleaned_data["operateur_paiement"]
            citoyen.save()

            messages.success(request, "Vos informations ont été mises à jour.")
            return redirect("citoyen_espace")
    else:
        form = ModifierProfilForm(user=request.user, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "telephone": citoyen.telephone,
            "operateur_paiement": citoyen.operateur_paiement,
        })

    return render(request, "citoyens/espace/modifier_profil.html", {
        "citoyen": citoyen,
        "form": form,
    })

@login_required
def declarations_liste_view(request):
    """Liste des declarations fiscales deposees par le citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    declarations = []
    if profil:
        declarations = (
            DeclarationFiscale.objects.filter(contribuable=profil.contribuable)
            .select_related("parcelle", "type_taxe")
            .order_by("-date_declaration")
        )

    return render(request, "citoyens/espace/declarations_liste.html", {
        "declarations": declarations,
        "citoyen": citoyen,
        "active_section": "declarations",
    })


@login_required
def declaration_creer_view(request):
    """Formulaire de depot d'une nouvelle declaration fiscale."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(
            request,
            "Votre compte n'est pas encore relié à un dossier fiscal. "
            "Contactez la mairie pour effectuer une déclaration."
        )
        return redirect("citoyen_espace")

    # Les parcelles "a soi" sont celles deja liees via une taxation
    # existante (fonctionne aussi pour les comptes simules sans
    # Proprietaire officiellement rattache), plus celles du Proprietaire
    # lie le cas echeant (dossier reel).
    parcelles_qs = Parcelle.objects.filter(taxations__contribuable=profil.contribuable)
    if profil.contribuable.proprietaire is not None:
        parcelles_qs = parcelles_qs | Parcelle.objects.filter(proprietaire=profil.contribuable.proprietaire)
    parcelles_qs = parcelles_qs.distinct()

    if request.method == "POST":
        form = DeclarationFiscaleForm(request.POST, request.FILES, parcelles_qs=parcelles_qs)
        if form.is_valid():
            declaration = form.save(commit=False)
            declaration.contribuable = profil.contribuable
            declaration.save()
            messages.success(
                request,
                "Votre déclaration a bien été soumise. Elle sera examinée par un agent "
                "et donnera lieu à l'émission de votre taxation."
            )
            return redirect("citoyen_declarations")
    else:
        form = DeclarationFiscaleForm(parcelles_qs=parcelles_qs)

    return render(request, "citoyens/espace/declaration_form.html", {
        "form": form,
        "citoyen": citoyen,
        "active_section": "declarations",
    })


@login_required
def recours_liste_view(request):
    """Liste des recours/redressements fiscaux deposes par le citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    recours_liste = []
    if profil:
        recours_liste = (
            RecoursFiscal.objects.filter(contribuable=profil.contribuable)
            .select_related("taxation", "taxation__type_taxe", "taxation__parcelle")
            .order_by("-date_soumission")
        )

    return render(request, "citoyens/espace/recours_liste.html", {
        "recours_liste": recours_liste,
        "citoyen": citoyen,
        "active_section": "recours",
    })


@login_required
def recours_creer_view(request, taxation_pk):
    """Depot d'un recours (niveau 1) sur une taxation precise."""
    from foncier.models import Taxation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    taxation = get_object_or_404(Taxation, pk=taxation_pk, contribuable=profil.contribuable)

    if request.method == "POST":
        form = RecoursFiscalForm(request.POST, request.FILES)
        if form.is_valid():
            recours = form.save(commit=False)
            recours.taxation = taxation
            recours.contribuable = profil.contribuable
            recours.niveau = RecoursFiscal.NIVEAU_RECOURS
            recours.save()
            messages.success(request, "Votre contestation a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_recours_liste")
    else:
        form = RecoursFiscalForm()

    return render(request, "citoyens/espace/recours_form.html", {
        "form": form,
        "taxation": taxation,
        "citoyen": citoyen,
        "active_section": "recours",
        "est_redressement": False,
    })


@login_required
def recours_redressement_creer_view(request, recours_pk):
    """Depot d'un redressement (niveau 2) suite au rejet d'un recours."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    recours_precedent = get_object_or_404(
        RecoursFiscal,
        pk=recours_pk,
        contribuable=profil.contribuable,
        niveau=RecoursFiscal.NIVEAU_RECOURS,
        statut=RecoursFiscal.STATUT_REJETE,
    )

    if request.method == "POST":
        form = RecoursFiscalForm(request.POST, request.FILES)
        if form.is_valid():
            redressement = form.save(commit=False)
            redressement.taxation = recours_precedent.taxation
            redressement.contribuable = profil.contribuable
            redressement.niveau = RecoursFiscal.NIVEAU_REDRESSEMENT
            redressement.recours_precedent = recours_precedent
            redressement.save()
            messages.success(request, "Votre demande de redressement a bien été soumise.")
            return redirect("citoyen_recours_liste")
    else:
        form = RecoursFiscalForm()

    return render(request, "citoyens/espace/recours_form.html", {
        "form": form,
        "taxation": recours_precedent.taxation,
        "citoyen": citoyen,
        "active_section": "recours",
        "est_redressement": True,
        "recours_precedent": recours_precedent,
    })


@login_required
def calendrier_fiscal_view(request):
    """
    Calendrier des echeances fiscales du citoyen connecte. Reprend
    exactement la meme logique de calcul de date que la commande
    envoyer_rappels_echeances (foncier/management/commands/), pour que
    l'affichage reste toujours coherent avec les rappels reellement
    envoyes par SMS/email.
    """
    import datetime
    from foncier.models import Taxation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    echeances = []

    if profil:
        taxations = (
            Taxation.objects.filter(contribuable=profil.contribuable)
            .select_related("type_taxe", "parcelle")
            .exclude(type_taxe__mois_echeance__isnull=True)
            .exclude(type_taxe__jour_echeance__isnull=True)
        )
        aujourdhui = datetime.date.today()

        for t in taxations:
            try:
                date_echeance = datetime.date(
                    aujourdhui.year, t.type_taxe.mois_echeance, t.type_taxe.jour_echeance
                )
            except ValueError:
                continue

            jours_restants = (date_echeance - aujourdhui).days

            if t.solde <= 0:
                statut_calendrier = "payee"
            elif jours_restants < 0:
                statut_calendrier = "en_retard"
            elif jours_restants <= 30:
                statut_calendrier = "proche"
            else:
                statut_calendrier = "a_venir"

            echeances.append({
                "taxation": t,
                "date_echeance": date_echeance,
                "jours_restants": jours_restants,
                "statut_calendrier": statut_calendrier,
            })

        echeances.sort(key=lambda e: e["date_echeance"])

    return render(request, "citoyens/espace/calendrier_fiscal.html", {
        "echeances": echeances,
        "citoyen": citoyen,
        "active_section": "calendrier",
    })


# ============================================================
# CONNEXION SECURISEE — code a usage unique (OTP)
#
# Apres identifiant/mot de passe corrects, un code a 6 chiffres est
# envoye par SMS (si telephone connu) et par email, valable 5 minutes.
# La connexion Django n'a lieu qu'une fois ce code saisi correctement.
# Stockage temporaire du code en session (pas de nouveau modele/table).
# ============================================================

import random


def _generer_otp():
    return str(random.randint(100000, 999999))


def _envoyer_otp(user, code):
    from django.core.mail import send_mail
    from django.conf import settings
    from foncier.sms import envoyer_sms

    message = f"KEUR MASSAR NORD : votre code de connexion est {code}. Valable 5 minutes."

    citoyen = getattr(user, "citoyen", None)
    if citoyen is not None and citoyen.telephone:
        try:
            envoyer_sms(citoyen.telephone, message)
        except Exception:
            pass

    if user.email:
        try:
            send_mail(
                subject="[KEUR MASSAR NORD] Code de connexion",
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass


def otp_verify_view(request):
    """Page de saisie du code recu par SMS/email pour terminer la connexion."""
    import time
    from django.contrib.auth import login

    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("citoyen_login")

    erreur = None

    if request.method == "POST":
        code_saisi = request.POST.get("code", "").strip()
        expire = request.session.get("otp_expire", 0)

        if time.time() > expire:
            erreur = "Ce code a expiré. Veuillez vous reconnecter."
            for cle in ["otp_user_id", "otp_code", "otp_expire", "otp_next"]:
                request.session.pop(cle, None)
        elif code_saisi and code_saisi == request.session.get("otp_code"):
            user = User.objects.get(pk=user_id)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            next_url = request.session.pop("otp_next", None) or reverse("citoyen_espace")
            for cle in ["otp_user_id", "otp_code", "otp_expire"]:
                request.session.pop(cle, None)
            return redirect(next_url)
        else:
            erreur = "Code incorrect. Réessayez."

    return render(request, "citoyens/otp_verify.html", {"erreur": erreur})


def otp_resend_view(request):
    """Renvoie un nouveau code OTP (invalide l'ancien)."""
    import time

    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("citoyen_login")

    user = User.objects.get(pk=user_id)
    code = _generer_otp()
    request.session["otp_code"] = code
    request.session["otp_expire"] = time.time() + 300
    _envoyer_otp(user, code)
    messages.info(request, "Un nouveau code vous a été envoyé.")
    return redirect("citoyen_otp_verify")


@login_required
def exoneration_liste_view(request):
    """Liste des demandes d'exoneration fiscale deposees par le citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    demandes = []
    if profil:
        demandes = (
            DemandeExoneration.objects.filter(contribuable=profil.contribuable)
            .select_related("parcelle")
            .order_by("-date_soumission")
        )

    return render(request, "citoyens/espace/exoneration_liste.html", {
        "demandes": demandes,
        "citoyen": citoyen,
        "active_section": "exonerations",
    })


@login_required
def exoneration_creer_view(request, parcelle_pk):
    """Depot d'une demande d'exoneration fiscale pour une parcelle precise."""
    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    parcelles_qs = Parcelle.objects.filter(taxations__contribuable=profil.contribuable)
    if profil.contribuable.proprietaire is not None:
        parcelles_qs = parcelles_qs | Parcelle.objects.filter(proprietaire=profil.contribuable.proprietaire)
    parcelle = get_object_or_404(parcelles_qs.distinct(), pk=parcelle_pk)

    if request.method == "POST":
        form = DemandeExonerationForm(request.POST, request.FILES)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.contribuable = profil.contribuable
            demande.parcelle = parcelle
            demande.save()
            messages.success(request, "Votre demande d'exonération a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_exoneration_liste")
    else:
        form = DemandeExonerationForm()

    return render(request, "citoyens/espace/exoneration_form.html", {
        "form": form,
        "parcelle": parcelle,
        "citoyen": citoyen,
        "active_section": "exonerations",
    })


@login_required
def plan_paiement_liste_view(request):
    """Liste des plans de paiement du citoyen connecte, avec leurs echeances."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    plans = []
    if profil:
        plans = (
            PlanPaiement.objects.filter(contribuable=profil.contribuable)
            .select_related("taxation", "taxation__type_taxe", "taxation__parcelle")
            .prefetch_related("echeances")
            .order_by("-date_soumission")
        )

    return render(request, "citoyens/espace/plan_paiement_liste.html", {
        "plans": plans,
        "citoyen": citoyen,
        "active_section": "plans_paiement",
    })


@login_required
def plan_paiement_creer_view(request, taxation_pk):
    """Depot d'une demande de plan de paiement pour une taxation precise."""
    from foncier.models import Taxation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    taxation = get_object_or_404(Taxation, pk=taxation_pk, contribuable=profil.contribuable)

    if request.method == "POST":
        form = PlanPaiementForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.taxation = taxation
            plan.contribuable = profil.contribuable
            plan.save()
            messages.success(request, "Votre demande de plan de paiement a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_plan_paiement_liste")
    else:
        form = PlanPaiementForm()

    return render(request, "citoyens/espace/plan_paiement_form.html", {
        "form": form,
        "taxation": taxation,
        "citoyen": citoyen,
        "active_section": "plans_paiement",
    })


@login_required
def echeance_payer_view(request, echeance_pk):
    """
    Paiement d'une echeance precise d'un plan de paiement valide.
    Reprend exactement le meme mecanisme que payer_taxation_view : le
    paiement reste 'En attente' jusqu'a validation par un agent (voir
    dashboard_paiement_valider, qui met egalement a jour cette echeance
    et le plan une fois confirme).
    """
    from foncier.models import EcheancePlanPaiement
    from foncier.paiement_gateway import initier_paiement

    profil = getattr(request.user, "profil_citoyen", None)
    if profil is None or not profil.actif:
        raise PermissionDenied("Votre compte n'est pas encore relié à un dossier contribuable.")

    echeance = get_object_or_404(
        EcheancePlanPaiement.objects.select_related("plan", "plan__taxation"),
        pk=echeance_pk, plan__contribuable=profil.contribuable,
    )

    if echeance.statut == "PAYEE":
        messages.info(request, "Cette échéance est déjà réglée.")
        return redirect("citoyen_plan_paiement_liste")

    if request.method == "POST":
        form = PaiementEnLigneForm(request.POST)
        if form.is_valid():
            resultat = initier_paiement(
                taxation=echeance.plan.taxation,
                montant=echeance.montant,
                telephone=form.cleaned_data["telephone"],
                request=request,
                backend=form.cleaned_data["operateur"],
            )
            if not resultat["ok"]:
                messages.error(request, resultat["erreur"] or "Le paiement n'a pas pu être initié.")
            else:
                echeance.paiement = resultat["paiement"]
                echeance.save(update_fields=["paiement"])

                if resultat["redirect_url"]:
                    return redirect(resultat["redirect_url"])
                return redirect("citoyen_paiement_retour", pk=resultat["paiement"].pk)
    else:
        initial = {}
        citoyen = getattr(request.user, "citoyen", None)
        if citoyen is not None:
            if citoyen.operateur_paiement:
                initial["operateur"] = citoyen.operateur_paiement
            if citoyen.telephone:
                initial["telephone"] = citoyen.telephone
        form = PaiementEnLigneForm(initial=initial)

    return render(request, "citoyens/espace/echeance_payer.html", {
        "echeance": echeance,
        "form": form,
    })


@login_required
def demande_payer_view(request, pk):
    """
    Paiement du tarif d'une demarche payante (extrait cadastral...).
    Reste 'En attente' jusqu'a validation par un agent, comme les
    paiements fiscaux (voir TraitementDemandeForm.statut_paiement).
    """
    import uuid

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    demande = get_object_or_404(DemandeService, pk=pk, demandeur=request.user)

    if not demande.type_demande.tarif or demande.type_demande.tarif <= 0:
        messages.info(request, "Cette démarche est gratuite, aucun paiement n'est nécessaire.")
        return redirect("citoyen_demande_detail", pk=demande.pk)

    if demande.statut_paiement == "CONFIRME":
        messages.info(request, "Cette démarche est déjà payée.")
        return redirect("citoyen_demande_detail", pk=demande.pk)

    if request.method == "POST":
        form = PaiementEnLigneForm(request.POST)
        if form.is_valid():
            demande.montant_paye = demande.type_demande.tarif
            demande.reference_paiement = f"DEMO-{uuid.uuid4().hex[:10].upper()}"
            demande.statut_paiement = "EN_ATTENTE"
            demande.save(update_fields=["montant_paye", "reference_paiement", "statut_paiement"])
            messages.success(request, "Votre paiement a bien été enregistré. Il sera validé par un agent sous peu.")
            return redirect("citoyen_demande_detail", pk=demande.pk)
    else:
        initial = {}
        if citoyen.operateur_paiement:
            initial["operateur"] = citoyen.operateur_paiement
        if citoyen.telephone:
            initial["telephone"] = citoyen.telephone
        form = PaiementEnLigneForm(initial=initial)

    return render(request, "citoyens/demandes/demande_payer.html", {
        "demande": demande,
        "form": form,
        "citoyen": citoyen,
    })


@login_required
def morcellement_fusion_liste_view(request):
    """Liste des demandes de morcellement/fusion du citoyen connecte."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    demandes = (
        DemandeMorcellementFusion.objects.filter(demandeur=request.user)
        .prefetch_related("parcelles_concernees", "parcelles_resultantes")
        .order_by("-date_soumission")
    )

    return render(request, "citoyens/espace/morcellement_fusion_liste.html", {
        "demandes": demandes,
        "citoyen": citoyen,
        "active_section": "morcellement_fusion",
    })


@login_required
def morcellement_fusion_creer_view(request):
    """Depot d'une demande de morcellement ou de fusion de parcelle(s)."""
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    parcelles_qs = _parcelles_du_citoyen_qs(request.user)

    if request.method == "POST":
        form = DemandeMorcellementFusionForm(request.POST, request.FILES, parcelles_qs=parcelles_qs)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            form.save_m2m()
            messages.success(request, "Votre demande a bien été soumise. Elle sera examinée par un agent.")
            return redirect("citoyen_morcellement_fusion_liste")
    else:
        form = DemandeMorcellementFusionForm(parcelles_qs=parcelles_qs)

    return render(request, "citoyens/espace/morcellement_fusion_form.html", {
        "form": form,
        "citoyen": citoyen,
        "active_section": "morcellement_fusion",
    })


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
