CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_import = "from .forms import ContribuableForm, PaiementForm"
nouveau_import = "from .forms import ContribuableForm, PaiementForm\nfrom .forms import DemandeImmatriculationForm"

if "DemandeImmatriculationForm" in contenu.split("def ")[0]:
    print("DEJA FAIT : import deja present.")
elif ancre_import in contenu:
    contenu = contenu.replace(ancre_import, nouveau_import, 1)
    changements += 1
    print("OK : import DemandeImmatriculationForm ajoute.")
else:
    print("ERREUR : ligne d'import introuvable.")

AJOUT = '''

def immatriculation_demande_view(request):
    """
    Formulaire PUBLIC (aucun compte requis) permettant a une personne
    qui n'a jamais ete contribuable de demander sa premiere
    immatriculation fiscale, pour une parcelle deja cadastree mais pas
    encore rattachee a un proprietaire/contribuable connu.
    """
    if request.method == "POST":
        form = DemandeImmatriculationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Votre demande a bien été soumise. Un agent l'examinera et vous "
                "recevrez votre numéro fiscal par email une fois votre dossier validé."
            )
            return redirect("immatriculation_demande")
    else:
        form = DemandeImmatriculationForm()

    return render(request, "foncier/immatriculation_demande.html", {
        "form": form,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def immatriculation_demande_view" in contenu_a_jour:
    print("DEJA FAIT : vue deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vue immatriculation_demande_view ajoutee.")

print(f"\n=== {changements} changement(s) enregistres. ===")