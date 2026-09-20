CHEMIN = "citoyens/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

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
'''

if "class DemandeExonerationForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : DemandeExonerationForm ajoute a la fin du fichier.")