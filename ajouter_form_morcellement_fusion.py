CHEMIN = "citoyens/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

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
'''

if "class DemandeMorcellementFusionForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : DemandeMorcellementFusionForm ajoute a la fin du fichier.")