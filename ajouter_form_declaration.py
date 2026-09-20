CHEMIN = "citoyens/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

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
'''

if "class DeclarationFiscaleForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : DeclarationFiscaleForm ajoute a la fin du fichier.")