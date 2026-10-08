# Lance ce script depuis la racine de ton projet Django (dossier contenant manage.py)
# Execution : powershell -ExecutionPolicy Bypass -File setup_jeunesse_app.ps1

New-Item -ItemType Directory -Force -Path "jeunesse\migrations" | Out-Null
New-Item -ItemType Directory -Force -Path "jeunesse\templates\jeunesse\emails" | Out-Null

@'

'@ | Set-Content -Path "jeunesse\__init__.py" -Encoding UTF8

@'
from django.apps import AppConfig


class JeunesseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jeunesse"
'@ | Set-Content -Path "jeunesse\apps.py" -Encoding UTF8

@'
from django.conf import settings
from django.db import models


class ProjetJeune(models.Model):
    STATUT_EN_ATTENTE = "en_attente"
    STATUT_VALIDE = "valide"
    STATUT_REJETE = "rejete"
    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, "En attente d'étude"),
        (STATUT_VALIDE, "Validé par la mairie"),
        (STATUT_REJETE, "Non retenu"),
    ]

    SECTEUR_CHOICES = [
        ("AGRICULTURE", "Agriculture / Élevage"),
        ("COMMERCE", "Commerce"),
        ("ARTISANAT", "Artisanat"),
        ("NUMERIQUE", "Numérique / Tech"),
        ("EDUCATION", "Éducation / Formation"),
        ("SANTE", "Santé"),
        ("ENVIRONNEMENT", "Environnement / Assainissement"),
        ("CULTURE", "Culture / Sport"),
        ("AUTRE", "Autre"),
    ]

    BESOIN_CHOICES = [
        ("FINANCEMENT", "Financement"),
        ("LOCAL", "Local / Terrain"),
        ("FORMATION", "Formation / Accompagnement"),
        ("RESEAU", "Mise en réseau / Partenaires"),
        ("MATERIEL", "Matériel / Équipement"),
        ("AUTRE", "Autre besoin"),
    ]

    # Porteur de projet (pas de compte requis pour soumettre)
    nom_porteur = models.CharField("Nom complet", max_length=150)
    age = models.PositiveIntegerField("Âge", null=True, blank=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    quartier = models.CharField("Quartier à Keur Massar Nord", max_length=150, blank=True)

    # Le projet
    titre_projet = models.CharField(max_length=200)
    secteur = models.CharField(max_length=20, choices=SECTEUR_CHOICES, default="AUTRE")
    description = models.TextField()
    besoin_principal = models.CharField(max_length=20, choices=BESOIN_CHOICES, default="AUTRE")
    details_besoin = models.TextField("Précisions sur le besoin", blank=True)

    # Suivi / validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="projets_jeunes_traites"
    )
    motif_rejet = models.TextField(blank=True)
    contacte = models.BooleanField("Contacté par la mairie", default=False)

    class Meta:
        verbose_name = "Projet jeune"
        verbose_name_plural = "Projets jeunes"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"{self.titre_projet} — {self.nom_porteur}"


class MessageProjet(models.Model):
    """Message envoyé par la mairie au porteur de projet (par email)."""
    projet = models.ForeignKey(ProjetJeune, on_delete=models.CASCADE, related_name="messages")
    contenu = models.TextField()
    envoye_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_envoi"]

    def __str__(self):
        return f"Message à {self.projet.nom_porteur} du {self.date_envoi:%d/%m/%Y}"


class RessourceJeune(models.Model):
    """Fiche d'information : aides, dispositifs, contacts utiles pour entreprendre."""
    CATEGORIES = [
        ("FINANCEMENT", "Financement"),
        ("FORMATION", "Formation / Accompagnement"),
        ("FONCIER", "Foncier / Local"),
        ("RESEAU", "Réseau / Partenaires"),
        ("ADMINISTRATIF", "Démarches administratives"),
    ]

    titre = models.CharField(max_length=150)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField()
    lien = models.URLField(blank=True, help_text="Lien externe (site officiel, formulaire...)")
    contact = models.CharField(max_length=200, blank=True, help_text="Téléphone/email de contact, si utile")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Ressource jeunesse"
        verbose_name_plural = "Ressources jeunesse"
        ordering = ["categorie", "ordre", "titre"]

    def __str__(self):
        return self.titre
'@ | Set-Content -Path "jeunesse\models.py" -Encoding UTF8

@'
from django import forms

from .models import ProjetJeune, MessageProjet


class ProjetJeuneForm(forms.ModelForm):
    class Meta:
        model = ProjetJeune
        fields = [
            "nom_porteur", "age", "telephone", "email", "quartier",
            "titre_projet", "secteur", "description",
            "besoin_principal", "details_besoin",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "details_besoin": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        telephone = cleaned.get("telephone")
        email = cleaned.get("email")
        if not telephone and not email:
            raise forms.ValidationError(
                "Merci d'indiquer au moins un moyen de contact (téléphone ou email)."
            )
        return cleaned


class MessageProjetForm(forms.ModelForm):
    class Meta:
        model = MessageProjet
        fields = ["contenu"]
        widgets = {
            "contenu": forms.Textarea(attrs={"rows": 4, "placeholder": "Votre message au porteur de projet..."}),
        }
'@ | Set-Content -Path "jeunesse\forms.py" -Encoding UTF8

@'
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
        form = ProjetJeuneForm(request.POST)
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
'@ | Set-Content -Path "jeunesse\views.py" -Encoding UTF8

@'
from django.contrib import admin

from .models import ProjetJeune, MessageProjet, RessourceJeune


class MessageProjetInline(admin.TabularInline):
    model = MessageProjet
    extra = 0
    readonly_fields = ("envoye_par", "date_envoi")


@admin.register(ProjetJeune)
class ProjetJeuneAdmin(admin.ModelAdmin):
    list_display = ("titre_projet", "nom_porteur", "secteur", "statut", "contacte", "date_soumission")
    list_filter = ("statut", "secteur", "besoin_principal", "contacte")
    search_fields = ("titre_projet", "nom_porteur", "telephone", "email")
    inlines = [MessageProjetInline]


@admin.register(RessourceJeune)
class RessourceJeuneAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "ordre")
    list_filter = ("categorie",)
'@ | Set-Content -Path "jeunesse\admin.py" -Encoding UTF8

@'
from django.urls import path

from . import views

urlpatterns = [
    path("", views.espace_jeunes_accueil, name="espace_jeunes"),
    path("soumettre/", views.soumettre_projet, name="jeunesse_soumettre"),
    path("merci/", views.merci_projet, name="jeunesse_merci"),
    path("ressources/", views.ressources_jeunes, name="jeunesse_ressources"),

    # Gestion (agents)
    path("gestion/projets-jeunes/", views.gestion_projets_jeunes, name="gestion_projets_jeunes"),
]
'@ | Set-Content -Path "jeunesse\urls.py" -Encoding UTF8

@'

'@ | Set-Content -Path "jeunesse\migrations\__init__.py" -Encoding UTF8

@'
{% extends 'foncier/base.html' %}
{% block title %}Espace Jeunes - KEUR MASSAR NORD{% endblock %}

{% block extra_head %}
<style>
  .ej-hero {
    background: linear-gradient(135deg, var(--green-dark, #1f5c3a), var(--green, #2f7a4f));
    color: #fff; border-radius: 16px; padding: 40px 32px; margin-bottom: 28px;
  }
  .ej-hero h1 { font-size: 26px; margin-bottom: 10px; }
  .ej-hero p { font-size: 15px; opacity: .95; max-width: 640px; }
  .ej-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
  .ej-card {
    border: 1px solid #e9ecef; border-radius: 14px; padding: 22px; background: #fff;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
  }
  .ej-card i { font-size: 22px; color: var(--green, #2f7a4f); margin-bottom: 10px; display:block; }
  .ej-card h3 { font-size: 16px; margin-bottom: 8px; }
  .ej-card p { font-size: 13.5px; color: #6c757d; margin-bottom: 14px; }
  .ej-card a.btn { display:inline-block; }
</style>
{% endblock %}

{% block content %}
<section class="container page-section">
  <div class="ej-hero">
    <h1>Espace Jeunes — Keur Massar Nord</h1>
    <p>
      Un projet, une idée pour ton quartier ? La mairie de Keur Massar Nord t'accompagne.
      Soumets ton projet, découvre les ressources disponibles pour entreprendre,
      et échange directement avec l'administration communale.
    </p>
  </div>

  <div class="ej-cards">
    <div class="ej-card">
      <i class="fa-solid fa-lightbulb"></i>
      <h3>Soumettre mon projet</h3>
      <p>Présente ton projet (agriculture, commerce, numérique, artisanat...) et tes besoins pour le réaliser.</p>
      <a href="{% url 'jeunesse_soumettre' %}" class="btn btn-primary">Je soumets mon projet</a>
    </div>

    <div class="ej-card">
      <i class="fa-solid fa-hand-holding-dollar"></i>
      <h3>Ressources & dispositifs</h3>
      <p>Financements, formations, accompagnement : les dispositifs disponibles pour les jeunes entrepreneurs.</p>
      <a href="{% url 'jeunesse_ressources' %}" class="btn btn-outline-secondary">Voir les ressources</a>
    </div>

    <div class="ej-card">
      <i class="fa-solid fa-comments"></i>
      <h3>Échanger avec la mairie</h3>
      <p>Une fois ton projet soumis, l'administration peut te contacter directement pour en discuter.</p>
      <a href="{% url 'contact' %}" class="btn btn-outline-secondary">Nous contacter</a>
    </div>
  </div>
</section>
{% endblock %}
'@ | Set-Content -Path "jeunesse\templates\jeunesse\accueil.html" -Encoding UTF8

@'
{% extends 'foncier/base.html' %}
{% block title %}Soumettre mon projet - Espace Jeunes{% endblock %}

{% block extra_head %}
<style>
  .ej-form-wrap { max-width: 640px; margin: 0 auto; }
  .ej-field { margin-bottom: 16px; }
  .ej-field label { display:block; font-size:13px; font-weight:600; margin-bottom:6px; }
  .ej-field input, .ej-field select, .ej-field textarea {
    width:100%; padding:10px 12px; border:1px solid #dee2e6; border-radius:8px; font-size:14px;
  }
  .ej-field .helptext { font-size: 12px; color:#6c757d; margin-top:4px; }
  .ej-errors { color:#dc3545; font-size:12px; margin-top:4px; }
  .ej-row { display:flex; gap:14px; }
  .ej-row .ej-field { flex:1; }
  .ej-alert { background:#fbe9e6; border:1px solid #f2c9c2; color:#b23b2e; padding:12px 14px;
    border-radius:10px; margin-bottom:18px; font-size:13px; }
</style>
{% endblock %}

{% block content %}
<section class="container page-section">
  <div class="ej-form-wrap">
    <h1 style="font-size:22px; margin-bottom:6px;">Soumettre mon projet</h1>
    <p style="color:#6c757d; font-size:14px; margin-bottom:22px;">
      Décris ton projet, la mairie de Keur Massar Nord l'étudiera et pourra te recontacter.
    </p>

    {% if form.non_field_errors %}
      <div class="ej-alert">{{ form.non_field_errors.0 }}</div>
    {% endif %}

    <form method="post" novalidate>
      {% csrf_token %}

      <div class="ej-row">
        <div class="ej-field">
          <label for="{{ form.nom_porteur.id_for_label }}">Nom complet</label>
          {{ form.nom_porteur }}
          {% if form.nom_porteur.errors %}<div class="ej-errors">{{ form.nom_porteur.errors.0 }}</div>{% endif %}
        </div>
        <div class="ej-field">
          <label for="{{ form.age.id_for_label }}">Âge</label>
          {{ form.age }}
        </div>
      </div>

      <div class="ej-row">
        <div class="ej-field">
          <label for="{{ form.telephone.id_for_label }}">Téléphone</label>
          {{ form.telephone }}
          {% if form.telephone.errors %}<div class="ej-errors">{{ form.telephone.errors.0 }}</div>{% endif %}
        </div>
        <div class="ej-field">
          <label for="{{ form.email.id_for_label }}">Email (optionnel)</label>
          {{ form.email }}
        </div>
      </div>

      <div class="ej-field">
        <label for="{{ form.quartier.id_for_label }}">Quartier</label>
        {{ form.quartier }}
      </div>

      <div class="ej-field">
        <label for="{{ form.titre_projet.id_for_label }}">Titre du projet</label>
        {{ form.titre_projet }}
        {% if form.titre_projet.errors %}<div class="ej-errors">{{ form.titre_projet.errors.0 }}</div>{% endif %}
      </div>

      <div class="ej-field">
        <label for="{{ form.secteur.id_for_label }}">Secteur</label>
        {{ form.secteur }}
      </div>

      <div class="ej-field">
        <label for="{{ form.description.id_for_label }}">Description du projet</label>
        {{ form.description }}
        {% if form.description.errors %}<div class="ej-errors">{{ form.description.errors.0 }}</div>{% endif %}
      </div>

      <div class="ej-field">
        <label for="{{ form.besoin_principal.id_for_label }}">Besoin principal</label>
        {{ form.besoin_principal }}
      </div>

      <div class="ej-field">
        <label for="{{ form.details_besoin.id_for_label }}">Précisions sur le besoin</label>
        {{ form.details_besoin }}
      </div>

      <button type="submit" class="btn btn-primary" style="width:100%; padding:12px;">
        Envoyer mon projet
      </button>
    </form>
  </div>
</section>
{% endblock %}
'@ | Set-Content -Path "jeunesse\templates\jeunesse\soumettre_projet.html" -Encoding UTF8

@'
{% extends 'foncier/base.html' %}
{% block title %}Projet envoyé - Espace Jeunes{% endblock %}

{% block content %}
<section class="container page-section" style="text-align:center; max-width:560px; margin:0 auto;">
  <i class="fa-solid fa-circle-check" style="font-size:44px; color:var(--green, #2f7a4f); margin-bottom:16px; display:block;"></i>
  <h1 style="font-size:22px; margin-bottom:10px;">Projet bien envoyé !</h1>
  <p style="color:#6c757d; font-size:14px; margin-bottom:24px;">
    Merci pour ta démarche. L'équipe de la mairie va étudier ton projet et pourra te
    contacter directement par téléphone ou email pour en discuter.
  </p>
  <a href="{% url 'jeunesse_ressources' %}" class="btn btn-outline-secondary">Voir les ressources disponibles</a>
  <a href="{% url 'espace_jeunes' %}" class="btn btn-primary" style="margin-left:8px;">Retour à l'Espace Jeunes</a>
</section>
{% endblock %}
'@ | Set-Content -Path "jeunesse\templates\jeunesse\merci.html" -Encoding UTF8

@'
{% extends 'foncier/base.html' %}
{% block title %}Ressources - Espace Jeunes{% endblock %}

{% block extra_head %}
<style>
  .res-cat { margin-bottom: 30px; }
  .res-cat h2 { font-size: 17px; color: var(--green, #2f7a4f); margin-bottom: 14px; }
  .res-item {
    border: 1px solid #e9ecef; border-radius: 12px; padding: 16px 18px; margin-bottom: 12px; background:#fff;
  }
  .res-item h4 { font-size: 15px; margin-bottom: 6px; }
  .res-item p { font-size: 13.5px; color:#6c757d; margin-bottom: 8px; }
  .res-item .meta { font-size: 12.5px; color: var(--green, #2f7a4f); }
  .res-empty { color:#6c757d; font-size:14px; }
</style>
{% endblock %}

{% block content %}
<section class="container page-section">
  <h1 style="font-size:22px; margin-bottom:6px;">Ressources pour jeunes entrepreneurs</h1>
  <p style="color:#6c757d; font-size:14px; margin-bottom:26px;">
    Dispositifs, financements et contacts utiles pour réaliser ton projet à Keur Massar Nord.
  </p>

  {% if par_categorie %}
    {% for categorie, ressources in par_categorie.items %}
      <div class="res-cat">
        <h2>{{ categorie }}</h2>
        {% for r in ressources %}
          <div class="res-item">
            <h4>{{ r.titre }}</h4>
            <p>{{ r.description }}</p>
            {% if r.contact %}<div class="meta"><i class="fa-solid fa-phone"></i> {{ r.contact }}</div>{% endif %}
            {% if r.lien %}<div class="meta"><a href="{{ r.lien }}" target="_blank" rel="noopener">{{ r.lien }}</a></div>{% endif %}
          </div>
        {% endfor %}
      </div>
    {% endfor %}
  {% else %}
    <p class="res-empty">Aucune ressource publiée pour l'instant.</p>
  {% endif %}
</section>
{% endblock %}
'@ | Set-Content -Path "jeunesse\templates\jeunesse\ressources.html" -Encoding UTF8

@'
{% load static %}
{# ------------------------------------------------------------------
   Adapte {% extends %} pour hériter du template de base de ton
   dashboard de gestion, par ex : {% extends "dashboard/base.html" %}
------------------------------------------------------------------ #}
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gestion — Projets Jeunes · KEUR MASSAR NORD Admin</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    :root {
        --ink: #24201a; --ink-quiet: #766c5d; --border: #e7e0d3;
        --bg: #f8f5ef; --card: #ffffff; --green: #2f7a4f; --amber: #b9740b; --red: #b23b2e;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--ink); padding: 32px 24px; }
    h1 { font-size: 20px; margin: 0 0 4px; }
    .page-sub { color: var(--ink-quiet); font-size: 13px; margin-bottom: 24px; }
    .alert { border-radius: 10px; padding: 11px 15px; margin-bottom: 18px; font-size: 13px;
      background: #eaf4ee; border: 1px solid #c9e5d4; color: var(--green); }
    .panel { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; margin-bottom: 26px; }
    .panel h2 { font-size: 14px; text-transform: uppercase; letter-spacing: .04em; color: var(--ink-quiet); margin: 0 0 16px; }

    .projet-card { border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 14px; }
    .projet-card .top { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; flex-wrap:wrap; }
    .projet-card h3 { font-size: 15px; margin: 0 0 4px; }
    .projet-card .meta { font-size: 12.5px; color: var(--ink-quiet); }
    .projet-card .desc { font-size: 13.5px; margin: 10px 0; line-height:1.5; }

    .badge { display:inline-block; padding:3px 9px; border-radius:999px; font-size:11px; font-weight:600; }
    .badge.en_attente { background:#fdf1de; color:var(--amber); }
    .badge.valide { background:#eaf4ee; color:var(--green); }
    .badge.rejete { background:#fbe9e6; color:var(--red); }
    .badge.contacte { background:#e6effb; color:#2563eb; }

    .actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
    .btn { border:none; border-radius:8px; padding:7px 12px; font-size:12px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:6px; }
    .btn-valider { background: var(--green); color:#fff; }
    .btn-rejeter { background:#fff; color:var(--red); border:1px solid #f2c9c2; }
    .btn-contacte { background:#fff; color:#2563eb; border:1px solid #c7d7f5; }
    .btn-message { background:#fff; color:var(--ink); border:1px solid var(--border); }

    dialog { border:none; border-radius:12px; padding:20px; max-width:380px; width:90%; box-shadow: 0 20px 45px -15px rgba(0,0,0,0.3); }
    dialog::backdrop { background: rgba(0,0,0,0.4); }
    dialog textarea { width:100%; border:1px solid var(--border); border-radius:8px; padding:10px; font-size:13px; margin:10px 0; min-height:80px; }
    dialog .dialog-actions { display:flex; justify-content:flex-end; gap:8px; }
    .btn-secondary { background:#f1ede4; color:var(--ink); }

    .messages-list { margin-top:10px; border-top:1px dashed var(--border); padding-top:8px; }
    .messages-list .msg { font-size:12.5px; margin-bottom:6px; color:var(--ink-quiet); }
    .empty { color: var(--ink-quiet); font-size:13px; padding:16px 4px; }
  </style>
</head>
<body>

  <h1>Gestion — Projets Jeunes</h1>
  <div class="page-sub">Étudie les projets soumis, valide, contacte ou échange avec les porteurs de projet.</div>

  {% if messages %}
    {% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}
  {% endif %}

  <div class="panel">
    <h2>En attente ({{ projets_en_attente|length }})</h2>
    {% if projets_en_attente %}
      {% for projet in projets_en_attente %}
        <div class="projet-card">
          <div class="top">
            <div>
              <h3>{{ projet.titre_projet }}</h3>
              <div class="meta">
                {{ projet.nom_porteur }}{% if projet.age %} — {{ projet.age }} ans{% endif %}
                · {{ projet.get_secteur_display }} · {{ projet.quartier|default:"quartier non précisé" }}
                <br>{{ projet.telephone }}{% if projet.email %} · {{ projet.email }}{% endif %}
              </div>
            </div>
            <div>
              <span class="badge {{ projet.statut }}">{{ projet.get_statut_display }}</span>
              {% if projet.contacte %}<span class="badge contacte">Contacté</span>{% endif %}
            </div>
          </div>
          <div class="desc">{{ projet.description }}</div>
          <div class="meta"><strong>Besoin :</strong> {{ projet.get_besoin_principal_display }}
            {% if projet.details_besoin %} — {{ projet.details_besoin }}{% endif %}</div>

          <div class="actions">
            <form method="post" style="display:inline;">
              {% csrf_token %}
              <input type="hidden" name="projet_id" value="{{ projet.id }}">
              <input type="hidden" name="action" value="valider">
              <button type="submit" class="btn btn-valider"><i class="fa-solid fa-check"></i> Valider</button>
            </form>
            <button type="button" class="btn btn-rejeter" onclick="document.getElementById('reject-{{ projet.id }}').showModal()">
              <i class="fa-solid fa-xmark"></i> Non retenu
            </button>
            {% if not projet.contacte %}
              <form method="post" style="display:inline;">
                {% csrf_token %}
                <input type="hidden" name="projet_id" value="{{ projet.id }}">
                <input type="hidden" name="action" value="contacte">
                <button type="submit" class="btn btn-contacte"><i class="fa-solid fa-phone"></i> Marquer contacté</button>
              </form>
            {% endif %}
            <button type="button" class="btn btn-message" onclick="document.getElementById('msg-{{ projet.id }}').showModal()">
              <i class="fa-solid fa-message"></i> Envoyer un message
            </button>
          </div>

          {% if projet.messages.all %}
            <div class="messages-list">
              {% for m in projet.messages.all %}
                <div class="msg"><strong>{{ m.date_envoi|date:"d/m/Y H:i" }}</strong> — {{ m.contenu }}</div>
              {% endfor %}
            </div>
          {% endif %}

          <dialog id="reject-{{ projet.id }}">
            <form method="post">
              {% csrf_token %}
              <input type="hidden" name="projet_id" value="{{ projet.id }}">
              <input type="hidden" name="action" value="rejeter">
              <strong>Motif (non retenu)</strong>
              <textarea name="motif" placeholder="Ex : projet hors périmètre communal..."></textarea>
              <div class="dialog-actions">
                <button type="button" class="btn btn-secondary" onclick="document.getElementById('reject-{{ projet.id }}').close()">Annuler</button>
                <button type="submit" class="btn btn-rejeter">Confirmer</button>
              </div>
            </form>
          </dialog>

          <dialog id="msg-{{ projet.id }}">
            <form method="post">
              {% csrf_token %}
              <input type="hidden" name="projet_id" value="{{ projet.id }}">
              <input type="hidden" name="action" value="message">
              <strong>Message au porteur de projet</strong>
              {{ message_form.contenu }}
              <div class="dialog-actions">
                <button type="button" class="btn btn-secondary" onclick="document.getElementById('msg-{{ projet.id }}').close()">Annuler</button>
                <button type="submit" class="btn btn-valider">Envoyer</button>
              </div>
            </form>
          </dialog>
        </div>
      {% endfor %}
    {% else %}
      <div class="empty">Aucun projet en attente.</div>
    {% endif %}
  </div>

  <div class="panel">
    <h2>Historique</h2>
    {% if projets_traites %}
      {% for projet in projets_traites %}
        <div class="projet-card">
          <div class="top">
            <div>
              <h3>{{ projet.titre_projet }}</h3>
              <div class="meta">{{ projet.nom_porteur }} · {{ projet.get_secteur_display }}</div>
            </div>
            <span class="badge {{ projet.statut }}">{{ projet.get_statut_display }}</span>
          </div>
        </div>
      {% endfor %}
    {% else %}
      <div class="empty">Aucun projet traité pour le moment.</div>
    {% endif %}
  </div>

</body>
</html>
'@ | Set-Content -Path "jeunesse\templates\jeunesse\gestion_projets.html" -Encoding UTF8

@'
Bonjour {{ projet.nom_porteur }},

Nous avons bien reçu votre projet « {{ projet.titre_projet }} » via l'Espace Jeunes de Keur Massar Nord.

L'équipe de la mairie va l'étudier et pourra vous recontacter par téléphone ou email pour en discuter davantage.

Merci pour votre engagement dans le développement du quartier.

Cordialement,
L'administration — Commune de Keur Massar Nord
'@ | Set-Content -Path "jeunesse\templates\jeunesse\emails\projet_recu.txt" -Encoding UTF8

@'
Bonjour {{ projet.nom_porteur }},

Vous avez reçu un nouveau message de la mairie de Keur Massar Nord au sujet de votre projet « {{ projet.titre_projet }} » :

"{{ message_obj.contenu }}"

Vous pouvez répondre directement en contactant la mairie au numéro habituel, ou en répondant à cet email si une adresse de contact vous a été fournie.

Cordialement,
L'administration — Commune de Keur Massar Nord
'@ | Set-Content -Path "jeunesse\templates\jeunesse\emails\nouveau_message.txt" -Encoding UTF8

Write-Host "Fichiers de l'app jeunesse créés avec succès."
Write-Host "Étapes suivantes :"
Write-Host "1. Ajoute jeunesse dans INSTALLED_APPS (settings.py)"
Write-Host "2. Ajoute  path(jeunes/, include(jeunesse.urls))  dans ton urls.py principal"
Write-Host "3. python manage.py makemigrations jeunesse ; python manage.py migrate"