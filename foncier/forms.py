from django import forms
from .models import Contribuable, Paiement, Taxation, Propriétaire
from .models import MessageContact
from .models import Signalement
from .antispam import AntiSpamFormMixin
class ContribuableForm(forms.ModelForm):
    class Meta:
        model = Contribuable
        fields = [
            'proprietaire', 'numero_fiscal', 'nom', 'prenom',
            'telephone', 'quartier',
        ]
        widgets = {
            'proprietaire': forms.Select(attrs={'class': 'form-select'}),
            'numero_fiscal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : KMSN-2026-00214',
            }),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : 77 123 45 67',
            }),
            'quartier': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'proprietaire': 'Propriétaire lié (optionnel)',
            'numero_fiscal': 'Numéro fiscal communal',
            'quartier': 'Quartier de résidence / activité',
        }

    def clean_numero_fiscal(self):
        numero = self.cleaned_data['numero_fiscal'].strip()
        qs = Contribuable.objects.filter(numero_fiscal__iexact=numero)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce numéro fiscal est déjà utilisé par un autre contribuable.")
        return numero


class PaiementForm(forms.ModelForm):
    contribuable = forms.ModelChoiceField(
        queryset=Contribuable.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_contribuable'}),
        label="Contribuable",
    )

    class Meta:
        model = Paiement
        fields = ['taxation', 'montant', 'mode_paiement']
        widgets = {
            'taxation': forms.Select(attrs={'class': 'form-select', 'id': 'id_taxation'}),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1',
                'placeholder': 'Montant en FCFA',
            }),
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'taxation': 'Taxation concernée',
            'montant': 'Montant payé (FCFA)',
            'mode_paiement': 'Mode de paiement',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordonne les taxations par contribuable pour un select plus lisible
        self.fields['taxation'].queryset = Taxation.objects.select_related(
            'contribuable', 'type_taxe'
        ).order_by('contribuable__nom')

    def clean_montant(self):
        montant = self.cleaned_data['montant']
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return montant

    def clean(self):
        cleaned_data = super().clean()
        taxation = cleaned_data.get('taxation')
        montant = cleaned_data.get('montant')
        if taxation and montant and montant > taxation.solde:
            raise forms.ValidationError(
                f"Le montant dépasse le solde restant dû ({taxation.solde:.0f} FCFA)."
            )
        return cleaned_data



class ContactForm(AntiSpamFormMixin, forms.ModelForm):
    class Meta:
        model = MessageContact
        fields = ['nom', 'email', 'telephone', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre.email@exemple.com',
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+221 XX XXX XX XX (optionnel)',
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet de votre message',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Écrivez votre message ici...',
                'rows': 6,
            }),
        }
# -*- coding: utf-8 -*-
"""
Formulaire du simulateur fiscal — à intégrer dans forms.py de l'app 'foncier'.

Les choix et bornes ci-dessous reflètent les règles réelles du Code Général
des Impôts (CGI) du Sénégal (voir commentaires dans views.py pour les sources).
"""



class SimulateurFiscalForm(forms.Form):

    TYPE_CHOICES = [
        ("ir", "Impôt sur le Revenu (IR) — Particulier"),
        ("is", "Impôt sur les Sociétés (IS) — Entreprise"),
        ("tva", "TVA — 18 %"),
        ("cgu", "Contribution Globale Unique (CGU) — Petite entreprise"),
    ]

    SITUATION_CHOICES = [
        ("celibataire", "Célibataire / divorcé(e) / veuf(ve)"),
        ("marie", "Marié(e)"),
    ]

    SECTEUR_CHOICES = [
        ("bien", "Vente / livraison de biens (commerce)"),
        ("service", "Prestation de services"),
    ]

    type_simulation = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label="Type d'impôt",
    )

    # Pour IR : revenu net imposable annuel (après IPRES/CSS/abattement 30 %)
    # Pour IS : bénéfice imposable annuel
    # Pour TVA : chiffre d'affaires HT annuel
    # Pour CGU : chiffre d'affaires TTC annuel
    revenu = forms.DecimalField(
        min_value=0,
        max_digits=14,
        decimal_places=0,
        label="Revenu net imposable / Chiffre d'affaires annuel (FCFA)",
    )

    # Utilisé pour l'IS : chiffre d'affaires HT servant de base au calcul de l'IMF
    # (impôt minimum forfaitaire = 0,5 % du CA HT, plancher 500 000, plafond 5 000 000)
    chiffre_affaires_is = forms.DecimalField(
        min_value=0,
        max_digits=14,
        decimal_places=0,
        required=False,
        label="Chiffre d'affaires HT (pour le calcul de l'IMF, si IS)",
    )

    situation_familiale = forms.ChoiceField(
        choices=SITUATION_CHOICES,
        required=False,
        initial="celibataire",
        label="Situation familiale (IR)",
    )

    nombre_enfants = forms.IntegerField(
        min_value=0,
        max_value=12,
        required=False,
        initial=0,
        label="Nombre d'enfants à charge (IR)",
    )

    secteur_activite = forms.ChoiceField(
        choices=SECTEUR_CHOICES,
        required=False,
        initial="bien",
        label="Secteur d'activité (CGU)",
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("nombre_enfants") is None:
            cleaned["nombre_enfants"] = 0
        if not cleaned.get("situation_familiale"):
            cleaned["situation_familiale"] = "celibataire"
        if not cleaned.get("secteur_activite"):
            cleaned["secteur_activite"] = "bien"
        return cleaned
# ============================================================
# À COPIER DANS : foncier/forms.py (crée le fichier s'il n'existe pas encore)
# ============================================================



class SignalementForm(AntiSpamFormMixin, forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ['titre', 'description', 'lieu', 'photo', 'telephone', 'latitude', 'longitude']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ex : Dépôt d'ordures, éclairage défectueux..."
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "Décrivez le problème en quelques mots"
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ex : Mbeubeuss, Keur Massar Unité 2..."
            }),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+221 XX XXX XX XX (optionnel)',
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        labels = {
            'titre': 'Titre du signalement',
            'description': 'Description',
            'lieu': 'Lieu',
            'photo': 'Photo (optionnel)',
            'telephone': 'Téléphone (optionnel)',
        }
        help_texts = {
            'telephone': "Utilisé uniquement pour vous prévenir par SMS quand le problème est résolu. Jamais publié.",
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La photo dépasse la taille maximale de 5 Mo.")
            content_type = getattr(photo, 'content_type', '') or ''
            if content_type and not content_type.startswith('image/'):
                raise forms.ValidationError("Le fichier joint doit être une image.")
        return photo