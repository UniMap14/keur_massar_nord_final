CHEMIN = "foncier/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

from .models import DemandeImmatriculation


class DemandeImmatriculationForm(forms.ModelForm):
    """
    Formulaire PUBLIC (sans compte requis) de premiere immatriculation
    fiscale : une personne qui n'a jamais ete contribuable demande a
    etre enregistree pour une parcelle deja cadastree, en fournissant
    une piece justificative de propriete.
    """
    nicad_parcelle = forms.CharField(
        label="NICAD de la parcelle (numéro figurant sur votre titre/acte)",
        max_length=50,
    )

    class Meta:
        model = DemandeImmatriculation
        fields = [
            "nom", "prenom", "ni_cni", "telephone", "email",
            "occupation_declaree", "piece_jointe",
        ]
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Votre nom"}),
            "prenom": forms.TextInput(attrs={"placeholder": "Votre prénom"}),
            "ni_cni": forms.TextInput(attrs={"placeholder": "Numéro de votre carte d'identité"}),
            "telephone": forms.TextInput(attrs={"placeholder": "+221 XX XXX XX XX"}),
        }
        labels = {
            "ni_cni": "Numéro CNI",
            "telephone": "Téléphone",
            "email": "Email (facultatif)",
            "occupation_declaree": "Occupation actuelle/prévue de la parcelle",
            "piece_jointe": "Pièce justificative (acte de vente, titre foncier...)",
        }

    def clean_nicad_parcelle(self):
        from .models import Parcelle

        nicad = self.cleaned_data["nicad_parcelle"].strip()
        parcelle = Parcelle.objects.filter(nicad__iexact=nicad).first()

        if parcelle is None:
            raise forms.ValidationError(
                "Aucune parcelle ne correspond à ce NICAD. Vérifiez le numéro sur votre "
                "acte, ou contactez la mairie si vous pensez qu'il s'agit d'une erreur."
            )

        self._parcelle_trouvee = parcelle
        return nicad

    def clean_piece_jointe(self):
        fichier = self.cleaned_data.get("piece_jointe")
        if not fichier:
            raise forms.ValidationError("Une pièce justificative est obligatoire pour cette démarche.")
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

if "class DemandeImmatriculationForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : DemandeImmatriculationForm ajoute a la fin du fichier.")