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