from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from .forms import ProjetJeuneForm, MessageProjetForm
from .models import ProjetJeune, RessourceJeune


def _est_agent(user):
    return user.is_staff


def espace_jeunes_accueil(request):
    """Page d'accueil de l'Espace Jeunes : présentation + liens."""
    return render(request, "jeunesse/accueil.html")


def soumettre_projet(request):
    if request.method == "POST":
        form = ProjetJeuneForm(request.POST, request.FILES)
        if form.is_valid():
            projet = form.save()

            # Notifie l'administration
            try:
                send_mail(
                    subject=f"[Espace Jeunes] Nouveau projet : {projet.titre_projet}",
                    message=(
                        f"Nouveau projet soumis par {projet.nom_porteur}.\n\n"
                        f"Secteur : {projet.get_secteur_display()}\n"
                        f"Contact : {projet.telephone or '—'} / {projet.email or '—'}\n"
                        f"Besoin principal : {projet.get_besoin_principal_display()}\n\n"
                        f"Description :\n{projet.description}"
                    ),
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=[getattr(settings, "CONTACT_EMAIL", settings.DEFAULT_FROM_EMAIL)],
                    fail_silently=True,
                )
            except Exception:
                pass

            # Confirmation au porteur, si email fourni
            if projet.email:
                try:
                    corps = render_to_string("jeunesse/emails/projet_recu.txt", {"projet": projet})
                    send_mail(
                        subject="Votre projet a bien été reçu — Espace Jeunes KEUR MASSAR NORD",
                        message=corps,
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=[projet.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            return redirect("jeunesse_merci")
    else:
        form = ProjetJeuneForm()

    return render(request, "jeunesse/soumettre_projet.html", {"form": form})


def merci_projet(request):
    return render(request, "jeunesse/merci.html")


def ressources_jeunes(request):
    ressources = RessourceJeune.objects.all()
    par_categorie = {}
    for ressource in ressources:
        par_categorie.setdefault(ressource.get_categorie_display(), []).append(ressource)
    return render(request, "jeunesse/ressources.html", {"par_categorie": par_categorie})


@login_required
@user_passes_test(_est_agent)
def gestion_projets_jeunes(request):
    if request.method == "POST":
        projet_id = request.POST.get("projet_id")
        action = request.POST.get("action")
        projet = get_object_or_404(ProjetJeune, pk=projet_id)

        if action == "valider":
            projet.statut = ProjetJeune.STATUT_VALIDE
            projet.date_traitement = timezone.now()
            projet.traite_par = request.user
            projet.save()
            messages.success(request, f"Projet « {projet.titre_projet} » validé.")

        elif action == "rejeter":
            projet.statut = ProjetJeune.STATUT_REJETE
            projet.motif_rejet = request.POST.get("motif", "").strip()
            projet.date_traitement = timezone.now()
            projet.traite_par = request.user
            projet.save()
            messages.success(request, f"Projet « {projet.titre_projet} » marqué non retenu.")

        elif action == "contacte":
            projet.contacte = True
            projet.save(update_fields=["contacte"])
            messages.success(request, "Projet marqué comme contacté.")

        elif action == "message":
            form = MessageProjetForm(request.POST)
            if form.is_valid():
                message_obj = form.save(commit=False)
                message_obj.projet = projet
                message_obj.envoye_par = request.user
                message_obj.save()

                if projet.email:
                    try:
                        corps = render_to_string("jeunesse/emails/nouveau_message.txt", {
                            "projet": projet, "message_obj": message_obj,
                        })
                        send_mail(
                            subject=f"[Espace Jeunes] Message de la mairie — {projet.titre_projet}",
                            message=corps,
                            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                            recipient_list=[projet.email],
                            fail_silently=True,
                        )
                        messages.success(request, "Message envoyé au porteur de projet.")
                    except Exception:
                        messages.warning(request, "Message enregistré, mais l'email n'a pas pu être envoyé.")
                else:
                    messages.info(request, "Message enregistré (aucun email renseigné, contacter par téléphone).")

        return redirect("gestion_projets_jeunes")

    projets_en_attente = ProjetJeune.objects.filter(statut=ProjetJeune.STATUT_EN_ATTENTE)
    projets_traites = ProjetJeune.objects.exclude(statut=ProjetJeune.STATUT_EN_ATTENTE)[:50]

    return render(request, "jeunesse/gestion_projets.html", {
        "projets_en_attente": projets_en_attente,
        "projets_traites": projets_traites,
        "message_form": MessageProjetForm(),
    })