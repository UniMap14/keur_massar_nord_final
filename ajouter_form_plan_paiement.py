CHEMIN = "citoyens/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

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
'''

if "class PlanPaiementForm" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : PlanPaiementForm ajoute a la fin du fichier.")