from django import forms

from .models import ProjetJeune, MessageProjet
from foncier.antispam import AntiSpamFormMixin


class ProjetJeuneForm(AntiSpamFormMixin, forms.ModelForm):
    class Meta:
        model = ProjetJeune
        fields = [
            "nom_porteur", "age", "telephone", "email", "quartier",
            "titre_projet", "secteur", "description",
            "besoin_principal", "details_besoin", "cv",
        ]
        widgets = {
            "nom_porteur": forms.TextInput(attrs={"placeholder": "Ton nom et prénom"}),
            "age": forms.NumberInput(attrs={"placeholder": "Âge"}),
            "telephone": forms.TextInput(attrs={"placeholder": "+221 XX XXX XX XX"}),
            "email": forms.EmailInput(attrs={"placeholder": "ton.email@exemple.com"}),
            "quartier": forms.TextInput(attrs={"placeholder": "Ex : Darou Salam, Firdawsi..."}),
            "titre_projet": forms.TextInput(attrs={"placeholder": "Ex : Élevage de volailles à Darou Salam"}),
            "description": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Décris ton projet, à qui il s'adresse, et où tu en es aujourd'hui...",
            }),
            "details_besoin": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Précise ce dont tu as besoin pour avancer...",
            }),
            "cv": forms.ClearableFileInput(attrs={"accept": "application/pdf"}),
        }

    def clean_cv(self):
        cv = self.cleaned_data.get("cv")
        if cv:
            if not cv.name.lower().endswith(".pdf"):
                raise forms.ValidationError("Le CV doit être un fichier PDF.")
            if cv.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Le fichier dépasse la taille maximale de 5 Mo.")
        return cv

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