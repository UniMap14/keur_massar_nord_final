CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    class Meta:
        model = DemandeService
        fields = ["statut", "commentaire_agent", "agent_traitant"]
        widgets = {
            "commentaire_agent": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Message visible par le citoyen (motif de rejet, instructions de retrait...).",
            }),
        }
        labels = {
            "statut": "Statut du dossier",
            "commentaire_agent": "Message pour le citoyen",
        }'''

nouveau = '''    class Meta:
        model = DemandeService
        fields = ["statut", "statut_paiement", "commentaire_agent", "agent_traitant"]
        widgets = {
            "commentaire_agent": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Message visible par le citoyen (motif de rejet, instructions de retrait...).",
            }),
        }
        labels = {
            "statut": "Statut du dossier",
            "statut_paiement": "Statut du paiement",
            "commentaire_agent": "Message pour le citoyen",
        }'''

if nouveau in contenu:
    print("DEJA FAIT : deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : statut_paiement ajoute au formulaire de traitement des demandes.")
else:
    print("ERREUR : ancre introuvable.")