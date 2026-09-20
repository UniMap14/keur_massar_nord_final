CHEMIN = "foncier/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

from .models import DemandeMutation


class DemandeMutationForm(forms.ModelForm):
    """
    Formulaire PUBLIC (sans compte requis) de mutation fiscale :
    l'acheteur d'une parcelle deja immatriculee demande le transfert
    du dossier fiscal a son nom, avec une preuve d'achat.
    """
    nicad_parcelle = forms.CharField(
        label="NICAD de la parcelle achetée",
        max_length=50,
    )

    class Meta:
        model = DemandeMutation
        fields = [
            "nouveau_nom", "nouveau_prenom", "nouveau_cni", "nouveau_telephone",
            "nouveau_email", "piece_jointe",
        ]
        widgets = {
            "nouveau_nom": forms.TextInput(attrs={"placeholder": "Votre nom"}),
            "nouveau_prenom": forms.TextInput(attrs={"placeholder": "Votre prénom"}),
            "nouveau_cni": forms.TextInput(attrs={"placeholder": "Numéro de votre carte d'identité"}),
            "nouveau_telephone": forms.TextInput(attrs={"placeholder": "+221 XX XXX XX XX"}),
        }
        labels = {
            "nouveau_nom": "Nom",
            "nouveau_prenom": "Prénom",
            "nouveau_cni": "Numéro CNI",
            "nouveau_telephone": "Téléphone",
            "nouveau_email": "Email (facultatif)",
            "piece_jointe": "Acte de vente / preuve d'achat",
        }

    def clean_nicad_parcelle(self):
        from .models import Parcelle

        nicad = self.cleaned_data["nicad_parcelle"].strip()
        parcelle = Parcelle.objects.filter(nicad__iexact=nicad).first()

        if parcelle is None:
            raise forms.ValidationError(
                "Aucune parcelle ne correspond à ce NICAD. Vérifiez le numéro sur votre acte."
            )
        if parcelle.proprietaire_id is None:
            raise forms.ValidationError(
                "Cette parcelle n'a pas encore de propriétaire enregistré : utilisez plutôt "
                "« Devenir contribuable » (première immatriculation), pas la mutation."
            )

        self._parcelle_trouvee = parcelle
        return nicad

    def clean_piece_jointe(self):
        fichier = self.cleaned_data.get("piece_jointe")
        if not fichier:
            raise forms.ValidationError("Une preuve d'achat est obligatoire pour cette démarche.")
        if hasattr(fichier, "size") and fichier.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Le fichier dépasse la taille maximale de 10 Mo.")
        return fichier

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.parcelle = self._parcelle_trouvee
        if commit:
            instance.save()
        return instance
'''

if "class DemandeMutationForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : DemandeMutationForm ajoute a la fin du fichier.")