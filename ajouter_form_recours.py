CHEMIN = "citoyens/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

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
'''

if "class RecoursFiscalForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : RecoursFiscalForm ajoute a la fin du fichier.")