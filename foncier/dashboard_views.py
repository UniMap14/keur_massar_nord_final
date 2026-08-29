# ============================================================
# foncier/dashboard_views.py
#
# Vues du dashboard admin custom. Fichier séparé de views.py
# pour ne pas mélanger le site public et la partie admin.
#
# Toutes les vues sont protégées par staff_member_required :
# seuls les comptes avec is_staff=True peuvent y accéder ; les
# autres sont redirigés vers LOGIN_URL (défini dans settings.py).
# ============================================================

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.urls import reverse_lazy, reverse
from django import forms
from django.template.loader import render_to_string
from datetime import date, timedelta
import calendar
import json
from .widgets import LeafletPolygonWidget
from .sms import envoyer_sms
from .permissions import role_requis, a_role, libelle_role
from .permissions import GROUPE_SUPERVISEUR, GROUPE_FISCAL, GROUPE_TECHNIQUE, ROLE_VERS_GROUPE
from .models import (
    Parcelle,
    Propriétaire,
    Zone,
    Contribuable,
    TypeTaxe,
    Taxation,
    Paiement,
    ProfilCitoyen,
    MessageContact,
    CategorieInfrastructure,
    Infrastructure,
    Actualite,
    DemandeService,
    TypeDemande,
    Signalement,
)

from django.conf import settings
from django.core.mail import send_mail


def _fcfa(valeur):
    if valeur is None:
        valeur = 0
    return f"{valeur:,.0f} FCFA".replace(",", " ")


# ------------------------------------------------------------
# CONNEXION / DÉCONNEXION
# ------------------------------------------------------------

class DashboardLoginView(auth_views.LoginView):
    """
    Connexion commune : la même page sert aussi bien aux agents (staff)
    qu'aux citoyens, puisqu'ils n'ont ni les mêmes identifiants ni la
    même destination une fois connectés.
    """
    template_name = "dashboard/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        IMPORTANT : ne JAMAIS se fier au paramètre ?next= tel quel pour un
        citoyen. Un citoyen déjà connecté qui tombe sur /gestion/ (réservé
        aux agents) est redirigé ici avec ?next=/gestion/ ; s'il était
        renvoyé vers ce ?next=, il retomberait aussitôt sur /gestion/ qui
        le rejette à nouveau → boucle de redirection infinie. On ignore
        donc ?next= pour les non-agents et on les envoie systématiquement
        vers leur propre espace.
        """
        user = self.request.user
        if user.is_staff:
            return self.get_redirect_url() or reverse("dashboard_home")
        return reverse("citoyen_espace")

    def get_default_redirect_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse("dashboard_home")
        return reverse("citoyen_espace")

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_staff:
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


# ------------------------------------------------------------
# MOT DE PASSE OUBLIÉ (4 étapes)
#
# 1. DashboardPasswordResetView        -> saisie de l'email
# 2. DashboardPasswordResetDoneView    -> "email envoyé"
# 3. DashboardPasswordResetConfirmView -> saisie du nouveau mdp (lien reçu)
# 4. DashboardPasswordResetCompleteView-> confirmation finale
#
# Les templates vivent dans templates/registration/ et héritent
# de registration/_auth_base.html (même charte que login.html).
# ------------------------------------------------------------

class DashboardPasswordResetView(auth_views.PasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.txt"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("dashboard_password_reset_done")


class DashboardPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class DashboardPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("dashboard_password_reset_complete")


class DashboardPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


# ------------------------------------------------------------
# TABLEAU DE BORD (accueil)
# ------------------------------------------------------------

@staff_member_required(login_url='dashboard_login')
def dashboard_home(request):
    total_recouvre = Paiement.objects.aggregate(Sum("montant"))["montant__sum"] or 0
    total_du = Taxation.objects.aggregate(Sum("montant_du"))["montant_du__sum"] or 0
    parcelles_en_retard = Parcelle.objects.filter(statut_fiscal="EN_RETARD").count()
    total_proprios = Propriétaire.objects.count()

    derniers_paiements = (
        Paiement.objects.select_related("taxation", "taxation__contribuable")
        .order_by("-date_paiement")[:6]
    )

    top_retardaires = (
        Parcelle.objects.filter(statut_fiscal="EN_RETARD")
        .select_related("proprietaire", "zone")
        .order_by("-montant_taxe_annuelle")[:6]
    )

    taux_recouvrement = round((total_recouvre / total_du) * 100, 1) if total_du else 0

    # --- Graphique 1 : évolution des paiements sur les 12 derniers mois ---
    aujourd_hui = date.today()
    debut_periode = (aujourd_hui.replace(day=1) - timedelta(days=365)).replace(day=1)

    paiements_par_mois = (
        Paiement.objects.filter(date_paiement__gte=debut_periode)
        .annotate(mois=TruncMonth("date_paiement"))
        .values("mois")
        .annotate(total=Sum("montant"))
        .order_by("mois")
    )
    totaux_par_mois = {p["mois"]: float(p["total"] or 0) for p in paiements_par_mois}

    labels_mois, valeurs_mois = [], []
    mois_cursor = debut_periode
    for _ in range(12):
        labels_mois.append(f"{calendar.month_abbr[mois_cursor.month].capitalize()} {mois_cursor.year}")
        valeurs_mois.append(totaux_par_mois.get(mois_cursor, 0))
        annee = mois_cursor.year + (1 if mois_cursor.month == 12 else 0)
        mois = 1 if mois_cursor.month == 12 else mois_cursor.month + 1
        mois_cursor = date(annee, mois, 1)

    # --- Graphique 2 : recouvrement par zone ---
    zones_stats = []
    for zone in Zone.objects.order_by("nom"):
        parcelles_zone = Parcelle.objects.filter(zone=zone)
        du_zone = Taxation.objects.filter(parcelle__in=parcelles_zone).aggregate(t=Sum("montant_du"))["t"] or 0
        paye_zone = Paiement.objects.filter(taxation__parcelle__in=parcelles_zone).aggregate(t=Sum("montant"))["t"] or 0
        if du_zone > 0:
            zones_stats.append({
                "nom": zone.nom,
                "taux": round((paye_zone / du_zone) * 100, 1),
            })
    zones_stats.sort(key=lambda z: z["taux"])
    zones_stats = zones_stats[:10]

    # --- Graphique 3 : répartition des montants dus par type de taxe ---
    repartition_taxes = (
        Taxation.objects.values("type_taxe__libelle")
        .annotate(total=Sum("montant_du"))
        .order_by("-total")
    )
    labels_taxes = [r["type_taxe__libelle"] for r in repartition_taxes]
    valeurs_taxes = [float(r["total"] or 0) for r in repartition_taxes]

    context = {
        "active_section": "home",
        "nb_parcelles": Parcelle.objects.count(),
        "total_recouvre_fmt": _fcfa(total_recouvre),
        "reste_a_recouvrer_fmt": _fcfa(total_du - total_recouvre),
        "taux_recouvrement": taux_recouvrement,
        "parcelles_en_retard": parcelles_en_retard,
        "total_proprios": total_proprios,
        "derniers_paiements": derniers_paiements,
        "top_retardaires": top_retardaires,
        "chart_mois_labels": json.dumps(labels_mois),
        "chart_mois_valeurs": json.dumps(valeurs_mois),
        "chart_zones_labels": json.dumps([z["nom"] for z in zones_stats]),
        "chart_zones_valeurs": json.dumps([z["taux"] for z in zones_stats]),
        "chart_zones_has_data": len(zones_stats) > 0,
        "chart_taxes_labels": json.dumps(labels_taxes),
        "chart_taxes_valeurs": json.dumps(valeurs_taxes),
        "chart_taxes_has_data": len(labels_taxes) > 0,
    }
    return render(request, "dashboard/home.html", context)


# ------------------------------------------------------------
# FORMULAIRE PARCELLE
# ------------------------------------------------------------

class ParcelleForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = [
            "nicad",
            "proprietaire",
            "zone",
            "superficie",
            "type_document",
            "adresse_parcelle",
            "valeur_locative",
            "montant_taxe_annuelle",
            "statut_fiscal",
            "geom",
        ]
        widgets = {
            "geom": LeafletPolygonWidget(),
        }


# ------------------------------------------------------------
# CRUD PARCELLE — pattern à dupliquer pour les autres modèles
# ------------------------------------------------------------

@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_parcelle_list(request):
    q = request.GET.get("q", "").strip()
    statut = request.GET.get("statut_fiscal", "").strip()

    parcelles = Parcelle.objects.select_related("proprietaire", "zone").order_by("-id")

    if q:
        parcelles = parcelles.filter(
            Q(nicad__icontains=q)
            | Q(proprietaire__nom__icontains=q)
            | Q(proprietaire__prenom__icontains=q)
            | Q(adresse_parcelle__icontains=q)
        )

    if statut:
        parcelles = parcelles.filter(statut_fiscal=statut)

    context = {
        "active_section": "parcelles",
        "nb_parcelles": Parcelle.objects.count(),
        "parcelles": parcelles,
        "q": q,
        "statut": statut,
    }
    return render(request, "dashboard/parcelle_list.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_parcelle_create(request):
    if request.method == "POST":
        form = ParcelleForm(request.POST)
        if form.is_valid():
            parcelle = form.save()
            messages.success(request, f"Parcelle « {parcelle.nicad} » créée avec succès.")
            return redirect("dashboard_parcelle_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = ParcelleForm()

    context = {
        "active_section": "parcelles",
        "form": form,
        "mode": "create",
    }
    return render(request, "dashboard/parcelle_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_parcelle_update(request, pk):
    parcelle = get_object_or_404(Parcelle, pk=pk)

    if request.method == "POST":
        form = ParcelleForm(request.POST, instance=parcelle)
        if form.is_valid():
            form.save()
            messages.success(request, f"Parcelle « {parcelle.nicad} » mise à jour.")
            return redirect("dashboard_parcelle_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = ParcelleForm(instance=parcelle)
        form.fields["geom"].widget.exclude_pk = parcelle.pk

    context = {
        "active_section": "parcelles",
        "form": form,
        "mode": "update",
        "parcelle": parcelle,
    }
    return render(request, "dashboard/parcelle_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_parcelle_delete(request, pk):
    parcelle = get_object_or_404(Parcelle, pk=pk)

    if request.method == "POST":
        nicad = parcelle.nicad
        parcelle.delete()
        messages.success(request, f"Parcelle « {nicad} » supprimée.")
        return redirect("dashboard_parcelle_list")

    context = {
        "active_section": "parcelles",
        "parcelle": parcelle,
    }
    return render(request, "dashboard/parcelle_confirm_delete.html", context)


# ------------------------------------------------------------
# MESSAGES DE CONTACT
#
# - dashboard_message_list  : liste filtrable (tous / traités / non traités)
# - dashboard_message_detail: détail + formulaire de réponse par email
#
# Le formulaire de réponse comporte 2 champs : "sujet" et "corps",
# tel qu'utilisé dans message_detail.html (form.sujet / form.corps).
# L'envoi de la réponse marque automatiquement le message comme traité.
# ------------------------------------------------------------

class ReponseMessageForm(forms.Form):
    sujet = forms.CharField(
        label="Sujet de l'email",
        max_length=200,
    )
    corps = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 8}),
    )


@staff_member_required(login_url='dashboard_login')
def dashboard_message_list(request):
    filtre = request.GET.get("statut", "").strip()  # "" | "traite" | "non_traite"

    msgs = MessageContact.objects.order_by("-date_envoi")
    if filtre == "traite":
        msgs = msgs.filter(traite=True)
    elif filtre == "non_traite":
        msgs = msgs.filter(traite=False)

    context = {
        "active_section": "messages",
        "messages_contact": msgs,
        "filtre": filtre,
        "nb_non_traites": MessageContact.objects.filter(traite=False).count(),
    }
    return render(request, "dashboard/message_list.html", context)


@staff_member_required(login_url='dashboard_login')
def dashboard_message_detail(request, pk):
    message_contact = get_object_or_404(MessageContact, pk=pk)

    if request.method == "POST":
        form = ReponseMessageForm(request.POST)
        if form.is_valid():
            sujet = form.cleaned_data["sujet"]
            corps = form.cleaned_data["corps"]

            send_mail(
                subject=sujet,
                message=corps,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[message_contact.email],
                fail_silently=False,
            )

            message_contact.traite = True
            message_contact.save()

            messages.success(request, f"Réponse envoyée à {message_contact.email}.")
            return redirect("dashboard_message_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        # Pré-remplissage du sujet en mode "Re: ..." pour gagner du temps
        sujet_initial = (
            f"Re: {message_contact.sujet}" if message_contact.sujet else "Réponse à votre message"
        )
        form = ReponseMessageForm(initial={"sujet": sujet_initial})

    context = {
        "active_section": "messages",
        "message_contact": message_contact,
        "form": form,
    }
    return render(request, "dashboard/message_detail.html", context)


# ------------------------------------------------------------
# STUBS pour les autres sections du menu (affichage liste
# uniquement, pour l'instant). À transformer en CRUD complet en
# suivant exactement le pattern Parcelle ci-dessus.
# ------------------------------------------------------------

@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_proprietaire_list(request):
    q = request.GET.get("q", "").strip()
    proprietaires = Propriétaire.objects.order_by("nom", "prenom")

    if q:
        proprietaires = proprietaires.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(ni_cni__icontains=q)
        )

    lignes = [
        {"pk": p.pk, "cellules": [p.nom, p.prenom, p.ni_cni, p.telephone or "—"]}
        for p in proprietaires
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "proprietaires",
        "titre": "Propriétaires",
        "colonnes": ["Nom", "Prénom", "N° CNI", "Téléphone"],
        "objets": lignes,
        "recherche_active": True,
        "q": q,
        "create_url_name": "dashboard_proprietaire_create",
        "create_label": "Nouveau propriétaire",
        "update_url_name": "dashboard_proprietaire_update",
        "delete_url_name": "dashboard_proprietaire_delete",
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_zone_list(request):
    q = request.GET.get("q", "").strip()
    zones = Zone.objects.order_by("nom")

    if q:
        zones = zones.filter(nom__icontains=q)

    lignes = [{"pk": z.pk, "cellules": [z.nom, z.layer]} for z in zones]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "zones",
        "titre": "Zones",
        "colonnes": ["Nom de la zone", "Couche source"],
        "objets": lignes,
        "recherche_active": True,
        "q": q,
        # Pas de création manuelle : la géométrie vient de l'import shapefile
        # (voir foncier/import_zones.py). On peut seulement renommer/supprimer.
        "update_url_name": "dashboard_zone_update",
        "delete_url_name": "dashboard_zone_delete",
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_contribuable_list(request):
    q = request.GET.get("q", "").strip()
    contribuables = Contribuable.objects.select_related("proprietaire").order_by("nom", "prenom")

    if q:
        contribuables = contribuables.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(numero_fiscal__icontains=q)
        )

    lignes = [
        {"pk": c.pk, "cellules": [c.numero_fiscal, c.nom, c.prenom, c.telephone or "—", c.quartier or "—"]}
        for c in contribuables
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "contribuables",
        "titre": "Contribuables",
        "colonnes": ["N° fiscal", "Nom", "Prénom", "Téléphone", "Quartier"],
        "objets": lignes,
        "recherche_active": True,
        "q": q,
        "create_url_name": "dashboard_contribuable_create",
        "create_label": "Nouveau contribuable",
        "update_url_name": "dashboard_contribuable_update",
        "delete_url_name": "dashboard_contribuable_delete",
        "export_url_name": "dashboard_contribuable_export_csv",
    })


def _reponse_csv(nom_fichier, entetes, lignes):
    """Construit une réponse HTTP de fichier CSV, encodée pour s'ouvrir
    correctement dans Excel (accents inclus) sans configuration côté
    utilisateur : encodage UTF-8 avec BOM, séparateur point-virgule
    (celui attendu par la version française d'Excel)."""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
    response.write("\ufeff")  # BOM UTF-8, pour qu'Excel détecte l'encodage
    writer = csv.writer(response, delimiter=";")
    writer.writerow(entetes)
    writer.writerows(lignes)
    return response


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_contribuable_export_csv(request):
    q = request.GET.get("q", "").strip()
    contribuables = Contribuable.objects.select_related("proprietaire").order_by("nom", "prenom")
    if q:
        contribuables = contribuables.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(numero_fiscal__icontains=q)
        )

    lignes = [
        [c.numero_fiscal, c.nom, c.prenom, c.telephone or "", c.quartier or "",
         c.montant_du_total, c.montant_paye_total, c.solde_total, c.statut_global]
        for c in contribuables
    ]
    return _reponse_csv(
        "contribuables.csv",
        ["N° fiscal", "Nom", "Prénom", "Téléphone", "Quartier",
         "Montant dû total (FCFA)", "Montant payé total (FCFA)", "Solde (FCFA)", "Statut"],
        lignes,
    )


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_taxation_export_csv(request):
    taxations = Taxation.objects.select_related("contribuable", "type_taxe", "parcelle").order_by("-annee_fiscale")
    lignes = [
        [str(t.contribuable), t.type_taxe.libelle, t.annee_fiscale,
         t.parcelle.nicad if t.parcelle else "", t.montant_du, t.montant_paye, t.solde, t.statut]
        for t in taxations
    ]
    return _reponse_csv(
        "taxations.csv",
        ["Contribuable", "Type de taxe", "Année fiscale", "Parcelle (NICAD)",
         "Montant dû (FCFA)", "Montant payé (FCFA)", "Solde (FCFA)", "Statut"],
        lignes,
    )


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_paiement_export_csv(request):
    paiements = Paiement.objects.select_related("taxation", "taxation__contribuable").order_by("-date_paiement")
    lignes = [
        [p.numero_recu, str(getattr(p.taxation, "contribuable", "")), p.taxation.type_taxe.libelle,
         p.montant, p.date_paiement, p.get_mode_paiement_display(), p.get_statut_paiement_display(),
         p.reference_transaction or ""]
        for p in paiements
    ]
    return _reponse_csv(
        "paiements.csv",
        ["N° reçu", "Contribuable", "Type de taxe", "Montant (FCFA)", "Date", "Mode", "Statut", "Réf. transaction"],
        lignes,
    )


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_taxation_list(request):
    taxations = Taxation.objects.select_related("contribuable", "type_taxe").order_by("-annee_fiscale")

    lignes = [
        {
            "pk": t.pk,
            "cellules": [
                t.contribuable,
                t.type_taxe,
                t.annee_fiscale,
                _fcfa(t.montant_du),
            ]
        }
        for t in taxations
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "taxations",
        "titre": "Taxations",
        "colonnes": ["Contribuable", "Type de taxe", "Année fiscale", "Montant dû"],
        "objets": lignes,
        "create_url_name": "dashboard_taxation_create",
        "create_label": "Nouvelle taxation",
        "update_url_name": "dashboard_taxation_update",
        "delete_url_name": "dashboard_taxation_delete",
        "export_url_name": "dashboard_taxation_export_csv",
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_paiement_list(request):
    from django.utils.html import format_html

    paiements = Paiement.objects.select_related("taxation", "taxation__contribuable").order_by("-date_paiement")

    lignes = [
        {
            "pk": p.pk,
            "cellules": [
                format_html(
                    '<a href="{}" style="color:var(--green);font-weight:700;text-decoration:none;">'
                    '<i class="fa-solid fa-file-pdf"></i> {}</a>',
                    reverse("paiement_recu_pdf", args=[p.pk]), p.numero_recu,
                ),
                getattr(p.taxation, "contribuable", "—"),
                _fcfa(p.montant),
                p.date_paiement,
                p.get_mode_paiement_display(),
            ]
        }
        for p in paiements
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "paiements",
        "titre": "Paiements",
        "colonnes": ["N° reçu", "Contribuable", "Montant", "Date", "Mode"],
        "objets": lignes,
        "create_url_name": "dashboard_paiement_create",
        "create_label": "Nouveau paiement",
        "update_url_name": "dashboard_paiement_update",
        "delete_url_name": "dashboard_paiement_delete",
        "export_url_name": "dashboard_paiement_export_csv",
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_typetaxe_list(request):
    q = request.GET.get("q", "").strip()
    types_taxe = TypeTaxe.objects.order_by("libelle")

    if q:
        types_taxe = types_taxe.filter(libelle__icontains=q)

    lignes = [{"pk": t.pk, "cellules": [t.libelle, t.get_code_display()]} for t in types_taxe]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "types_taxe",
        "titre": "Types de taxe",
        "colonnes": ["Libellé", "Code"],
        "objets": lignes,
        "recherche_active": True,
        "q": q,
        "create_url_name": "dashboard_typetaxe_create",
        "create_label": "Nouveau type de taxe",
        "update_url_name": "dashboard_typetaxe_update",
        "delete_url_name": "dashboard_typetaxe_delete",
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_profil_list(request):
    profils = ProfilCitoyen.objects.select_related("user", "contribuable").order_by("-date_creation")

    lignes = [
        {
            "pk": p.pk,
            "cellules": [
                p.user,
                getattr(p, "contribuable", "—"),
                "Actif" if p.actif else "Inactif",
                p.date_creation,
            ]
        }
        for p in profils
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "profils",
        "titre": "Profils citoyens",
        "colonnes": ["Utilisateur", "Contribuable lié", "Statut", "Date de création"],
        "objets": lignes,
        "create_url_name": "dashboard_profil_create",
        "create_label": "Lier un citoyen",
        "update_url_name": "dashboard_profil_update",
        "delete_url_name": "dashboard_profil_delete",
    })


# ------------------------------------------------------------
# FORMULAIRES — FISCALITÉ / CONTRIBUABLES (CRUD complet)
# ------------------------------------------------------------

class ProprietaireForm(forms.ModelForm):
    class Meta:
        model = Propriétaire
        fields = ["nom", "prenom", "ni_cni", "telephone", "adresse"]
        widgets = {"adresse": forms.Textarea(attrs={"rows": 3})}


class ZoneRenameForm(forms.ModelForm):
    """La géométrie des zones vient de l'import shapefile : seul le nom est éditable ici."""
    class Meta:
        model = Zone
        fields = ["nom"]


class ContribuableForm(forms.ModelForm):
    class Meta:
        model = Contribuable
        fields = ["proprietaire", "numero_fiscal", "nom", "prenom", "telephone", "quartier"]


class TypeTaxeForm(forms.ModelForm):
    class Meta:
        model = TypeTaxe
        fields = ["code", "libelle", "description", "mois_echeance", "jour_echeance", "penalite_retard"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class TaxationForm(forms.ModelForm):
    class Meta:
        model = Taxation
        fields = ["contribuable", "type_taxe", "parcelle", "annee_fiscale", "montant_du"]


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ["taxation", "montant", "mode_paiement"]


class ProfilCitoyenForm(forms.ModelForm):
    class Meta:
        model = ProfilCitoyen
        fields = ["user", "contribuable", "actif"]


def _crud_views(model, form_class, list_url_name, titre, str_field="pk", roles=()):
    """Génère (create, update, delete) génériques pour un modèle simple, pour éviter
    de dupliquer 6 fois le même squelette de vues."""

    @staff_member_required(login_url='dashboard_login')
    def create_view(request):
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                obj = form.save()
                messages.success(request, f"{titre} « {obj} » créé(e) avec succès.")
                return redirect(list_url_name)
            messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
        else:
            form = form_class()
        return render(request, "dashboard/generic_form_stub.html", {
            "form": form, "mode": "create", "titre": titre, "list_url_name": list_url_name,
        })

    @staff_member_required(login_url='dashboard_login')
    def update_view(request, pk):
        obj = get_object_or_404(model, pk=pk)
        if request.method == "POST":
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                obj = form.save()
                messages.success(request, f"{titre} « {obj} » mis(e) à jour.")
                return redirect(list_url_name)
            messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
        else:
            form = form_class(instance=obj)
        return render(request, "dashboard/generic_form_stub.html", {
            "form": form, "mode": "update", "titre": titre, "list_url_name": list_url_name,
        })

    @staff_member_required(login_url='dashboard_login')
    def delete_view(request, pk):
        obj = get_object_or_404(model, pk=pk)
        if request.method == "POST":
            texte = str(obj)
            obj.delete()
            messages.success(request, f"{titre} « {texte} » supprimé(e).")
            return redirect(list_url_name)
        return render(request, "dashboard/generic_confirm_delete.html", {
            "titre": titre, "list_url_name": list_url_name, "objet_str": str(obj),
        })

    if roles:
        create_view = role_requis(*roles)(create_view)
        update_view = role_requis(*roles)(update_view)
        delete_view = role_requis(*roles)(delete_view)

    return create_view, update_view, delete_view


dashboard_proprietaire_create, dashboard_proprietaire_update, dashboard_proprietaire_delete = _crud_views(
    Propriétaire, ProprietaireForm, "dashboard_proprietaire_list", "Propriétaire", roles=('technique',)
)

_, dashboard_zone_update, dashboard_zone_delete = _crud_views(
    Zone, ZoneRenameForm, "dashboard_zone_list", "Zone", roles=('technique',)
)

dashboard_contribuable_create, dashboard_contribuable_update, dashboard_contribuable_delete = _crud_views(
    Contribuable, ContribuableForm, "dashboard_contribuable_list", "Contribuable", roles=('fiscal',)
)

dashboard_typetaxe_create, dashboard_typetaxe_update, dashboard_typetaxe_delete = _crud_views(
    TypeTaxe, TypeTaxeForm, "dashboard_typetaxe_list", "Type de taxe", roles=('fiscal',)
)

dashboard_taxation_create, dashboard_taxation_update, dashboard_taxation_delete = _crud_views(
    Taxation, TaxationForm, "dashboard_taxation_list", "Taxation", roles=('fiscal',)
)

dashboard_paiement_create, dashboard_paiement_update, dashboard_paiement_delete = _crud_views(
    Paiement, PaiementForm, "dashboard_paiement_list", "Paiement", roles=('fiscal',)
)

dashboard_profil_create, dashboard_profil_update, dashboard_profil_delete = _crud_views(
    ProfilCitoyen, ProfilCitoyenForm, "dashboard_profil_list", "Profil citoyen", roles=('fiscal',)
)


# ------------------------------------------------------------
# FORMULAIRES — INFRASTRUCTURES / CATÉGORIES / ACTUALITÉS
# ------------------------------------------------------------

class CategorieInfrastructureForm(forms.ModelForm):
    class Meta:
        model = CategorieInfrastructure
        fields = ["code", "label", "description", "texte_intro", "icone", "couleur", "ordre"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "texte_intro": forms.Textarea(attrs={"rows": 4}),
            "couleur": forms.TextInput(attrs={"type": "color"}),
        }


class InfrastructureForm(forms.ModelForm):
    class Meta:
        model = Infrastructure
        fields = ["categorie", "nom", "quartier", "statut", "latitude", "longitude", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ActualiteForm(forms.ModelForm):
    class Meta:
        model = Actualite
        fields = ["titre", "categorie", "chapo", "contenu", "photo", "date_publication", "publie"]
        widgets = {
            "chapo": forms.Textarea(attrs={"rows": 3}),
            "contenu": forms.Textarea(attrs={"rows": 8}),
            "date_publication": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }


# ------------------------------------------------------------
# CRUD CATÉGORIES D'INFRASTRUCTURE
# ------------------------------------------------------------

@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_categorie_list(request):
    q = request.GET.get("q", "").strip()
    categories = CategorieInfrastructure.objects.order_by("ordre", "label")

    if q:
        categories = categories.filter(Q(label__icontains=q) | Q(code__icontains=q))

    context = {
        "active_section": "categories_infra",
        "categories": categories,
        "q": q,
    }
    return render(request, "dashboard/categorie_list.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_categorie_create(request):
    if request.method == "POST":
        form = CategorieInfrastructureForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Catégorie « {cat.label} » créée avec succès.")
            return redirect("dashboard_categorie_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = CategorieInfrastructureForm()

    context = {"active_section": "categories_infra", "form": form, "mode": "create"}
    return render(request, "dashboard/categorie_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_categorie_update(request, pk):
    categorie = get_object_or_404(CategorieInfrastructure, pk=pk)

    if request.method == "POST":
        form = CategorieInfrastructureForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, f"Catégorie « {categorie.label} » mise à jour.")
            return redirect("dashboard_categorie_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = CategorieInfrastructureForm(instance=categorie)

    context = {"active_section": "categories_infra", "form": form, "mode": "update", "categorie": categorie}
    return render(request, "dashboard/categorie_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_categorie_delete(request, pk):
    categorie = get_object_or_404(CategorieInfrastructure, pk=pk)

    if request.method == "POST":
        label = categorie.label
        categorie.delete()
        messages.success(request, f"Catégorie « {label} » supprimée.")
        return redirect("dashboard_categorie_list")

    context = {"active_section": "categories_infra", "categorie": categorie}
    return render(request, "dashboard/categorie_confirm_delete.html", context)


# ------------------------------------------------------------
# CRUD INFRASTRUCTURES
# ------------------------------------------------------------

@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_infrastructure_list(request):
    q = request.GET.get("q", "").strip()
    categorie_id = request.GET.get("categorie", "").strip()
    statut = request.GET.get("statut", "").strip()

    infrastructures = Infrastructure.objects.select_related("categorie").order_by("categorie__ordre", "nom")

    if q:
        infrastructures = infrastructures.filter(Q(nom__icontains=q) | Q(quartier__icontains=q))

    if categorie_id:
        infrastructures = infrastructures.filter(categorie_id=categorie_id)

    if statut:
        infrastructures = infrastructures.filter(statut=statut)

    context = {
        "active_section": "infrastructures",
        "infrastructures": infrastructures,
        "toutes_categories": CategorieInfrastructure.objects.order_by("ordre", "label"),
        "statuts": Infrastructure.STATUTS,
        "q": q,
        "categorie_id": categorie_id,
        "statut": statut,
    }
    return render(request, "dashboard/infrastructure_list.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_infrastructure_create(request):
    if request.method == "POST":
        form = InfrastructureForm(request.POST)
        if form.is_valid():
            infra = form.save()
            messages.success(request, f"Infrastructure « {infra.nom} » créée avec succès.")
            return redirect("dashboard_infrastructure_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = InfrastructureForm()

    context = {"active_section": "infrastructures", "form": form, "mode": "create"}
    return render(request, "dashboard/infrastructure_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_infrastructure_update(request, pk):
    infra = get_object_or_404(Infrastructure, pk=pk)

    if request.method == "POST":
        form = InfrastructureForm(request.POST, instance=infra)
        if form.is_valid():
            form.save()
            messages.success(request, f"Infrastructure « {infra.nom} » mise à jour.")
            return redirect("dashboard_infrastructure_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = InfrastructureForm(instance=infra)

    context = {"active_section": "infrastructures", "form": form, "mode": "update", "infrastructure": infra}
    return render(request, "dashboard/infrastructure_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_infrastructure_delete(request, pk):
    infra = get_object_or_404(Infrastructure, pk=pk)

    if request.method == "POST":
        nom = infra.nom
        infra.delete()
        messages.success(request, f"Infrastructure « {nom} » supprimée.")
        return redirect("dashboard_infrastructure_list")

    context = {"active_section": "infrastructures", "infrastructure": infra}
    return render(request, "dashboard/infrastructure_confirm_delete.html", context)


# ------------------------------------------------------------
# CRUD ACTUALITÉS
# ------------------------------------------------------------

@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_actualite_list(request):
    filtre = request.GET.get("statut", "").strip()  # "" | "publie" | "brouillon"
    q = request.GET.get("q", "").strip()

    actualites = Actualite.objects.order_by("-date_publication")

    if q:
        actualites = actualites.filter(Q(titre__icontains=q) | Q(chapo__icontains=q))

    if filtre == "publie":
        actualites = actualites.filter(publie=True)
    elif filtre == "brouillon":
        actualites = actualites.filter(publie=False)

    context = {
        "active_section": "actualites",
        "actualites": actualites,
        "filtre": filtre,
        "q": q,
        "nb_brouillons": Actualite.objects.filter(publie=False).count(),
    }
    return render(request, "dashboard/actualite_list.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_actualite_create(request):
    if request.method == "POST":
        form = ActualiteForm(request.POST, request.FILES)
        if form.is_valid():
            actu = form.save()
            messages.success(request, f"Actualité « {actu.titre} » créée avec succès.")
            return redirect("dashboard_actualite_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = ActualiteForm()

    context = {"active_section": "actualites", "form": form, "mode": "create"}
    return render(request, "dashboard/actualite_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_actualite_update(request, pk):
    actu = get_object_or_404(Actualite, pk=pk)

    if request.method == "POST":
        form = ActualiteForm(request.POST, request.FILES, instance=actu)
        if form.is_valid():
            form.save()
            messages.success(request, f"Actualité « {actu.titre} » mise à jour.")
            return redirect("dashboard_actualite_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = ActualiteForm(instance=actu)

    context = {"active_section": "actualites", "form": form, "mode": "update", "actualite": actu}
    return render(request, "dashboard/actualite_form.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_actualite_delete(request, pk):
    actu = get_object_or_404(Actualite, pk=pk)

    if request.method == "POST":
        titre = actu.titre
        actu.delete()
        messages.success(request, f"Actualité « {titre} » supprimée.")
        return redirect("dashboard_actualite_list")

    context = {"active_section": "actualites", "actualite": actu}
    return render(request, "dashboard/actualite_confirm_delete.html", context)

# ------------------------------------------------------------
# DÉMARCHES EN LIGNE (côté agent)
# ------------------------------------------------------------

class TraitementDemandeForm(forms.ModelForm):
    agent_traitant = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True).order_by("username"),
        required=False,
        label="Agent assigné",
        empty_label="— Non assigné —",
    )

    class Meta:
        model = DemandeService
        fields = ["statut", "commentaire_agent", "agent_traitant"]
        widgets = {
            "commentaire_agent": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Message visible par le citoyen (motif de rejet, instructions de retrait...).",
            }),
        }
        labels = {
            "statut": "Statut du dossier",
            "commentaire_agent": "Message pour le citoyen",
        }


@staff_member_required(login_url='dashboard_login')
def dashboard_demande_list(request):
    filtre = request.GET.get("statut", "").strip()
    mes_dossiers = request.GET.get("mes_dossiers") == "1"

    demandes = DemandeService.objects.select_related(
        "type_demande", "demandeur", "parcelle", "agent_traitant"
    ).order_by("-date_demande")

    if filtre:
        demandes = demandes.filter(statut=filtre)
    if mes_dossiers:
        demandes = demandes.filter(agent_traitant=request.user)

    context = {
        "active_section": "demandes",
        "demandes": demandes,
        "filtre": filtre,
        "mes_dossiers": mes_dossiers,
        "statut_choices": DemandeService.STATUT_CHOICES,
        "nb_a_traiter": DemandeService.objects.filter(
            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS]
        ).count(),
        "nb_mes_dossiers": DemandeService.objects.filter(
            agent_traitant=request.user,
            statut__in=[DemandeService.STATUT_RECUE, DemandeService.STATUT_EN_COURS],
        ).count(),
    }
    return render(request, "dashboard/demande_list.html", context)


def _envoyer_email_demande_statut_maj(request, demande):
    """Prévient le citoyen (depuis le dashboard agent) que le statut de sa démarche a changé."""
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


def _envoyer_sms_demande_statut_maj(demande):
    """Complète la notification email par un SMS, si le citoyen a renseigné
    un numéro de téléphone sur son profil. Best-effort : n'importe quel échec
    est silencieux, l'email reste le canal de notification garanti."""
    try:
        telephone = demande.demandeur.citoyen.telephone
    except Exception:
        telephone = ""

    if telephone:
        envoyer_sms(
            telephone,
            f"KMS Nord : votre dossier {demande.numero_dossier} est maintenant "
            f"\"{demande.get_statut_display()}\".",
        )


@staff_member_required(login_url='dashboard_login')
def dashboard_demande_detail(request, pk):
    demande = get_object_or_404(
        DemandeService.objects.select_related("type_demande", "demandeur", "parcelle", "agent_traitant"),
        pk=pk,
    )

    if request.method == "POST":
        statut_avant = demande.statut
        form = TraitementDemandeForm(request.POST, instance=demande)
        if form.is_valid():
            demande = form.save()

            if demande.statut != statut_avant:
                try:
                    _envoyer_email_demande_statut_maj(request, demande)
                    _envoyer_sms_demande_statut_maj(demande)
                    messages.success(
                        request,
                        f"Dossier {demande.numero_dossier} mis à jour. "
                        f"Le citoyen a été prévenu par email."
                    )
                except Exception:
                    messages.warning(
                        request,
                        f"Dossier {demande.numero_dossier} mis à jour, mais l'email de "
                        f"notification n'a pas pu être envoyé au citoyen."
                    )
            else:
                messages.success(request, f"Dossier {demande.numero_dossier} mis à jour.")

            return redirect("dashboard_demande_list")
    else:
        initial = {}
        if not demande.agent_traitant_id:
            initial["agent_traitant"] = request.user
        form = TraitementDemandeForm(instance=demande, initial=initial)

    context = {
        "active_section": "demandes",
        "demande": demande,
        "form": form,
    }
    return render(request, "dashboard/demande_detail.html", context)


# ------------------------------------------------------------
# SIGNALEMENTS CITOYENS (côté agent)
#
# Ces signalements ne sont jamais affichés au public : ils sont
# déposés anonymement par les citoyens (formulaire public) et ne
# doivent être consultés/traités que par l'administration, ici.
# ------------------------------------------------------------

class TraitementSignalementForm(forms.ModelForm):
    agent_assigne = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True).order_by("username"),
        required=False,
        label="Agent assigné",
        empty_label="— Non assigné —",
    )

    class Meta:
        model = Signalement
        fields = ["statut", "commentaire_agent", "agent_assigne"]
        widgets = {
            "commentaire_agent": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Note interne pour l'équipe (jamais visible par le public).",
            }),
        }
        labels = {
            "statut": "Statut du signalement",
            "commentaire_agent": "Note interne",
        }


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_signalement_list(request):
    filtre = request.GET.get("statut", "").strip()
    mes_dossiers = request.GET.get("mes_dossiers") == "1"

    signalements = Signalement.objects.select_related("agent_assigne").order_by("-date_signalement")

    if filtre:
        signalements = signalements.filter(statut=filtre)
    if mes_dossiers:
        signalements = signalements.filter(agent_assigne=request.user)

    context = {
        "active_section": "signalements",
        "signalements": signalements,
        "filtre": filtre,
        "mes_dossiers": mes_dossiers,
        "nb_en_cours": Signalement.objects.filter(statut="EN_COURS").count(),
        "nb_mes_dossiers": Signalement.objects.filter(agent_assigne=request.user, statut="EN_COURS").count(),
    }
    return render(request, "dashboard/signalement_list.html", context)


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_signalement_detail(request, pk):
    signalement = get_object_or_404(Signalement, pk=pk)

    if request.method == "POST":
        statut_avant = signalement.statut
        form = TraitementSignalementForm(request.POST, instance=signalement)
        if form.is_valid():
            signalement = form.save()

            # SMS au citoyen uniquement s'il a laissé un numéro ET que le
            # signalement vient de passer à "Résolu" (pas à chaque
            # modification, pour ne pas le spammer).
            if (
                signalement.telephone
                and statut_avant != 'RESOLU'
                and signalement.statut == 'RESOLU'
            ):
                envoyer_sms(
                    signalement.telephone,
                    f"KMS Nord : votre signalement \"{signalement.titre}\" a été marqué "
                    f"comme résolu. Merci pour votre contribution.",
                )

            messages.success(request, "Signalement mis à jour.")
            return redirect("dashboard_signalement_list")
    else:
        initial = {}
        if not signalement.agent_assigne_id:
            initial["agent_assigne"] = request.user
        form = TraitementSignalementForm(instance=signalement, initial=initial)

    context = {
        "active_section": "signalements",
        "signalement": signalement,
        "form": form,
    }
    return render(request, "dashboard/signalement_detail.html", context)


# ------------------------------------------------------------
# GESTION DES AGENTS (rôles / permissions par service)
#
# Réservé aux Superviseurs (et superusers) : attribuer un rôle aux
# comptes staff détermine à quelles sections du dashboard ils ont
# accès (voir foncier/permissions.py).
# ------------------------------------------------------------

def _est_superviseur(user):
    return user.is_superuser or GROUPE_SUPERVISEUR in set(user.groups.values_list("name", flat=True))


class AttribuerRoleForm(forms.Form):
    ROLE_CHOICES = [
        ("", "Aucun rôle spécifique (accès complet, compte historique)"),
        ("superviseur", "Superviseur (accès à tout)"),
        ("fiscal", "Agent fiscal (contribuables, taxations, paiements)"),
        ("technique", "Agent technique (parcelles, infrastructures, signalements)"),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=False, label="Rôle")


@staff_member_required(login_url='dashboard_login')
def dashboard_agent_list(request):
    if not _est_superviseur(request.user):
        raise PermissionDenied("Seuls les superviseurs peuvent gérer les rôles des agents.")

    agents = User.objects.filter(is_staff=True).prefetch_related("groups").order_by("username")

    lignes = [
        {"pk": u.pk, "cellules": [u.username, u.get_full_name() or "—", u.email or "—", libelle_role(u)]}
        for u in agents
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "agents",
        "titre": "Agents",
        "colonnes": ["Identifiant", "Nom complet", "Email", "Rôle"],
        "objets": lignes,
        "update_url_name": "dashboard_agent_update",
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_agent_update(request, pk):
    if not _est_superviseur(request.user):
        raise PermissionDenied("Seuls les superviseurs peuvent gérer les rôles des agents.")

    agent = get_object_or_404(User, pk=pk, is_staff=True)
    noms_groupes_roles = {GROUPE_SUPERVISEUR, GROUPE_FISCAL, GROUPE_TECHNIQUE}
    role_actuel = ""
    for nom, cle in [(GROUPE_SUPERVISEUR, "superviseur"), (GROUPE_FISCAL, "fiscal"), (GROUPE_TECHNIQUE, "technique")]:
        if agent.groups.filter(name=nom).exists():
            role_actuel = cle
            break

    if request.method == "POST":
        form = AttribuerRoleForm(request.POST)
        if form.is_valid():
            # Retire l'agent de tous les groupes de rôle, puis l'ajoute
            # au nouveau (ou aucun, si "Aucun rôle spécifique" choisi).
            agent.groups.remove(*Group.objects.filter(name__in=noms_groupes_roles))
            role = form.cleaned_data["role"]
            if role:
                groupe, _ = Group.objects.get_or_create(name=ROLE_VERS_GROUPE[role])
                agent.groups.add(groupe)
            messages.success(request, f"Rôle mis à jour pour {agent.username}.")
            return redirect("dashboard_agent_list")
    else:
        form = AttribuerRoleForm(initial={"role": role_actuel})

    return render(request, "dashboard/agent_form.html", {
        "active_section": "agents",
        "agent": agent,
        "form": form,
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_journal_audit_list(request):
    if not _est_superviseur(request.user):
        raise PermissionDenied("Seuls les superviseurs peuvent consulter le journal d'audit.")

    from .models import JournalAudit

    entrees = JournalAudit.objects.select_related("utilisateur").all()

    modele_filtre = request.GET.get("modele", "").strip()
    action_filtre = request.GET.get("action", "").strip()
    utilisateur_filtre = request.GET.get("utilisateur", "").strip()

    if modele_filtre:
        entrees = entrees.filter(modele=modele_filtre)
    if action_filtre:
        entrees = entrees.filter(action=action_filtre)
    if utilisateur_filtre:
        entrees = entrees.filter(utilisateur_id=utilisateur_filtre)

    paginator = Paginator(entrees, 50)
    page = paginator.get_page(request.GET.get("page"))

    modeles_disponibles = (
        JournalAudit.objects.values_list("modele", flat=True).distinct().order_by("modele")
    )
    utilisateurs_disponibles = (
        User.objects.filter(actions_audit__isnull=False).distinct().order_by("username")
    )

    return render(request, "dashboard/journal_audit_list.html", {
        "active_section": "journal_audit",
        "page": page,
        "modeles_disponibles": modeles_disponibles,
        "utilisateurs_disponibles": utilisateurs_disponibles,
        "modele_filtre": modele_filtre,
        "action_filtre": action_filtre,
        "utilisateur_filtre": utilisateur_filtre,
    })
