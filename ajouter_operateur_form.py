CHEMIN = "citoyens/forms.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    first_name = forms.CharField(label="Prénom", max_length=150, required=True)
    last_name = forms.CharField(label="Nom", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)
    telephone = forms.CharField(label="Téléphone", max_length=20, required=False)'''

nouveau = '''    first_name = forms.CharField(label="Prénom", max_length=150, required=True)
    last_name = forms.CharField(label="Nom", max_length=150, required=True)
    email = forms.EmailField(label="Email", required=True)
    telephone = forms.CharField(label="Téléphone", max_length=20, required=False)
    operateur_paiement = forms.ChoiceField(
        label="Opérateur de paiement enregistré",
        choices=[("", "— Non renseigné —")] + Citoyen.OPERATEURS_PAIEMENT,
        required=False,
        help_text="Pré-rempli automatiquement lors du paiement de vos taxations.",
    )'''

if "operateur_paiement" in contenu and "class ModifierProfilForm" in contenu:
    print("DEJA FAIT : champ deja present dans le formulaire.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champ operateur_paiement ajoute au formulaire.")
else:
    print("ERREUR : ancre introuvable.")