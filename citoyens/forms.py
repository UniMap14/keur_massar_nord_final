from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Citoyen
from foncier.antispam import AntiSpamFormMixin

User = get_user_model()


class CitoyenRegistrationForm(AntiSpamFormMixin, UserCreationForm):
    first_name = forms.CharField(label="Prénom", max_length=150)
    last_name = forms.CharField(label="Nom", max_length=150)
    email = forms.EmailField(label="Email")
    telephone = forms.CharField(label="Téléphone", max_length=20, required=False)
    numero_fiscal = forms.CharField(label="Identifiant fiscalité")
    numero_foncier = forms.CharField(label="Identifiant foncier (NICAD)")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cet email.")
        return email

    def clean_numero_fiscal(self):
        valeur = self.cleaned_data["numero_fiscal"].strip()
        if Citoyen.objects.filter(numero_fiscal__iexact=valeur).exists():
            raise forms.ValidationError("Cet identifiant fiscalité est déjà associé à un compte.")
        return valeur

    def clean_numero_foncier(self):
        valeur = self.cleaned_data["numero_foncier"].strip()
        if Citoyen.objects.filter(numero_foncier__iexact=valeur).exists():
            raise forms.ValidationError("Cet identifiant foncier est déjà associé à un compte.")
        return valeur

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        # Le compte Django est actif dès l'inscription : c'est le statut du
        # profil Citoyen (en_attente / valide / rejete) qui bloque réellement
        # l'accès à l'espace personnel tant que l'administration n'a pas validé.
        user.is_active = True
        if commit:
            user.save()
            Citoyen.objects.create(
                user=user,
                telephone=self.cleaned_data.get("telephone", ""),
                numero_fiscal=self.cleaned_data["numero_fiscal"],
                numero_foncier=self.cleaned_data["numero_foncier"],
            )
        return user

from foncier.models import DemandeService, TypeDemande


class DemandeServiceForm(forms.ModelForm):
    """Formulaire pour qu'un citoyen dépose une nouvelle démarche en ligne."""

    class Meta:
        model = DemandeService
        fields = ["type_demande", "parcelle", "objet", "piece_jointe"]
        widgets = {
            "objet": forms.Textarea(attrs={"rows": 4, "placeholder": "Précisez votre demande (facultatif)…"}),
        }
        labels = {
            "type_demande": "Type de démarche",
            "parcelle": "Parcelle concernée",
            "objet": "Précisions",
            "piece_jointe": "Pièce jointe (facultatif)",
        }

    def __init__(self, *args, parcelles_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type_demande"].queryset = TypeDemande.objects.filter(actif=True)
        self.fields["type_demande"].empty_label = "— Choisir une démarche —"
        self.fields["parcelle"].required = False
        self.fields["parcelle"].empty_label = "— Aucune parcelle précise —"
        if parcelles_qs is not None:
            self.fields["parcelle"].queryset = parcelles_qs
        else:
            self.fields["parcelle"].queryset = self.fields["parcelle"].queryset.none()

    def clean_piece_jointe(self):
        fichier = self.cleaned_data.get("piece_jointe")
        if fichier and hasattr(fichier, "size") and fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Le fichier dépasse la taille maximale de 10 Mo.")
        return fichier


class PaiementEnLigneForm(forms.Form):
    """Choix de l'opérateur de paiement en ligne pour régler une taxation."""
    OPERATEURS = [
        ('orange_money', 'Orange Money'),
        ('wave', 'Wave'),
    ]
    operateur = forms.ChoiceField(
        choices=OPERATEURS,
        widget=forms.RadioSelect,
        label="Opérateur",
    )
    telephone = forms.CharField(
        label="Numéro de téléphone",
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': '+221 XX XXX XX XX',
            'class': 'form-control',
        }),
        help_text="Le numéro associé à votre compte Orange Money ou Wave.",
    )


class ModifierProfilForm(forms.Form):
    """
    Permet au citoyen de modifier lui-même ses informations personnelles
    (identité, contact). Volontairement EXCLUS de ce formulaire : le nom
    d'utilisateur, l'identifiant fiscalité et l'identifiant foncier — ce
    sont des identifiants officiels que seule l'administration peut
    corriger (voir dashboard agent), pour éviter qu'un citoyen ne casse
    le lien avec son dossier fiscal en se trompant.
    """
    first_name = forms.CharField(label="Prénom", max_length=150, required=True)
    last_name = forms.CharField(label="Nom", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)
    telephone = forms.CharField(label="Téléphone", max_length=20, required=False)
    operateur_paiement = forms.ChoiceField(
        label="Opérateur de paiement enregistré",
        choices=[("", "— Non renseigné —")] + Citoyen.OPERATEURS_PAIEMENT,
        required=False,
        help_text="Pré-rempli automatiquement lors du paiement de vos taxations.",
    )

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = User.objects.filter(email__iexact=email)
        if self._user is not None:
            qs = qs.exclude(pk=self._user.pk)
        if qs.exists():
            raise forms.ValidationError("Un autre compte utilise déjà cet email.")
        return email

from foncier.models import DeclarationFiscale


class DeclarationFiscaleForm(forms.ModelForm):
    """Formulaire pour qu'un citoyen declare l'occupation d'une de ses
    parcelles, en vue du calcul de sa taxation par un agent (principe
    de la teledeclaration : le contribuable declare, l'administration
    valide et emet la taxe)."""

    class Meta:
        model = DeclarationFiscale
        fields = [
            "parcelle", "type_taxe", "annee_fiscale", "occupation_declaree",
            "superficie_declaree", "commentaire_citoyen", "piece_jointe",
        ]
        widgets = {
            "commentaire_citoyen": forms.Textarea(attrs={"rows": 4, "placeholder": "Précisions utiles (facultatif)…"}),
        }
        labels = {
            "parcelle": "Parcelle concernée",
            "type_taxe": "Type de taxe",
            "annee_fiscale": "Année fiscale",
            "occupation_declaree": "Occupation du sol déclarée",
            "superficie_declaree": "Superficie déclarée (m²)",
            "commentaire_citoyen": "Précisions",
            "piece_jointe": "Pièce jointe (facultatif)",
        }

    def __init__(self, *args, parcelles_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parcelle"].empty_label = "— Choisir une parcelle —"
        if parcelles_qs is not None:
            self.fields["parcelle"].queryset = parcelles_qs
        else:
            self.fields["parcelle"].queryset = self.fields["parcelle"].queryset.none()
        self.fields["superficie_declaree"].required = False
        self.fields["commentaire_citoyen"].required = False
        self.fields["piece_jointe"].required = False

    def clean_piece_jointe(self):
        fichier = self.cleaned_data.get("piece_jointe")
        if fichier and hasattr(fichier, "size") and fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Le fichier dépasse la taille maximale de 10 Mo.")
        return fichier


from foncier.models import RecoursFiscal


class RecoursFiscalForm(forms.ModelForm):
    """Formulaire pour qu'un citoyen conteste une taxation precise (le
    champ 'taxation' est fixe par la vue via l'URL, jamais par le
    formulaire -- on ne laisse jamais le citoyen choisir librement
    quelle taxation il conteste dans un simple menu deroulant)."""

    class Meta:
        model = RecoursFiscal
        fields = ["motif", "piece_jointe"]
        widgets = {
            "motif": forms.Textarea(attrs={"rows": 5, "placeholder": "Expliquez pourquoi vous contestez ce montant…"}),
        }
        labels = {
            "motif": "Motif de la contestation",
            "piece_jointe": "Pièce jointe (facultatif)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["piece_jointe"].required = False

    def clean_piece_jointe(self):
        fichier = self.cleaned_data.get("piece_jointe")
        if fichier and hasattr(fichier, "size") and fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Le fichier dépasse la taille maximale de 10 Mo.")
        return fichier


from foncier.models import DemandeExoneration


class DemandeExonerationForm(forms.ModelForm):
    """Formulaire pour qu'un citoyen demande l'exoneration fiscale
    d'une de ses parcelles (le champ 'parcelle' est fixe par la vue
    via l'URL, jamais par le formulaire)."""

    class Meta:
        model = DemandeExoneration
        fields = ["motif", "description", "piece_jointe"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Précisions utiles (facultatif)…"}),
        }
        labels = {
            "motif": "Motif de l'exonération",
            "description": "Précisions",
            "piece_jointe": "Pièce justificative",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

    def clean_piece_jointe(self):
        fichier = self.cleaned_data.get("piece_jointe")
        if not fichier:
            raise forms.ValidationError("Une pièce justificative est obligatoire pour cette démarche.")
        if hasattr(fichier, "size") and fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Le fichier dépasse la taille maximale de 10 Mo.")
        return fichier


from foncier.models import PlanPaiement


class PlanPaiementForm(forms.ModelForm):
    """Formulaire pour qu'un citoyen demande un echelonnement de
    paiement (le champ 'taxation' est fixe par la vue via l'URL)."""

    class Meta:
        model = PlanPaiement
        fields = ["nombre_echeances", "motif"]
        widgets = {
            "nombre_echeances": forms.Select(
                choices=[(2, "2 échéances"), (3, "3 échéances"), (4, "4 échéances")]
            ),
            "motif": forms.Textarea(attrs={"rows": 4, "placeholder": "Expliquez votre situation…"}),
        }
        labels = {
            "nombre_echeances": "Nombre d'échéances souhaité",
            "motif": "Motif de la demande",
        }


from foncier.models import DemandeMorcellementFusion


class DemandeMorcellementFusionForm(forms.ModelForm):
    """
    Formulaire pour qu'un citoyen demande le morcellement (division)
    d'une de ses parcelles, ou la fusion de plusieurs d'entre elles.
    Le queryset de 'parcelles_concernees' est restreint a celles du
    citoyen connecte (voir la vue).
    """
    parcelles_concernees = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label="Parcelle(s) concernée(s)",
        help_text="Une seule parcelle pour un morcellement ; au moins deux, adjacentes, pour une fusion.",
    )

    class Meta:
        model = DemandeMorcellementFusion
        fields = ["type_operation", "parcelles_concernees", "justification", "piece_jointe"]
        widgets = {
            "justification": forms.Textarea(attrs={"rows": 4, "placeholder": "Expliquez le motif de votre demande…"}),
        }
        labels = {
            "type_operation": "Type d'opération",
            "justification": "Motif de la demande",
            "piece_jointe": "Plan du géomètre / document justificatif",
        }

    def __init__(self, *args, parcelles_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parcelles_concernees"].queryset = parcelles_qs

    def clean(self):
        cleaned_data = super().clean()
        type_operation = cleaned_data.get("type_operation")
        parcelles = cleaned_data.get("parcelles_concernees")

        if type_operation and parcelles:
            if type_operation == DemandeMorcellementFusion.TYPE_MORCELLEMENT and parcelles.count() != 1:
                raise forms.ValidationError("Un morcellement concerne exactement UNE parcelle.")
            if type_operation == DemandeMorcellementFusion.TYPE_FUSION and parcelles.count() < 2:
                raise forms.ValidationError("Une fusion nécessite au moins DEUX parcelles.")

        return cleaned_data

    def clean_piece_jointe(self):
        fichier = self.cleaned_data.get("piece_jointe")
        if not fichier:
            raise forms.ValidationError("Un document justificatif est obligatoire pour cette démarche.")
        if hasattr(fichier, "size") and fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Le fichier dépasse la taille maximale de 10 Mo.")
        return fichier
