CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_import = "from .forms import DemandeImmatriculationForm"
nouveau_import = "from .forms import DemandeImmatriculationForm\nfrom .forms import DemandeMutationForm"

if "DemandeMutationForm" in contenu.split("def ")[0]:
    print("DEJA FAIT : import deja present.")
elif ancre_import in contenu:
    contenu = contenu.replace(ancre_import, nouveau_import, 1)
    changements += 1
    print("OK : import DemandeMutationForm ajoute.")
else:
    print("ERREUR : ligne d'import introuvable.")

AJOUT = '''

def mutation_demande_view(request):
    """
    Formulaire PUBLIC (aucun compte requis) permettant a l'acheteur
    d'une parcelle deja immatriculee de demander le transfert du
    dossier fiscal a son nom (mutation fiscale suite a une revente).
    """
    if request.method == "POST":
        form = DemandeMutationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Votre demande de mutation a bien été soumise. Un agent l'examinera et vous "
                "recevrez votre numéro fiscal par email une fois votre dossier validé."
            )
            return redirect("mutation_demande")
    else:
        form = DemandeMutationForm()

    return render(request, "foncier/mutation_demande.html", {
        "form": form,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def mutation_demande_view" in contenu_a_jour:
    print("DEJA FAIT : vue deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vue mutation_demande_view ajoutee.")

print(f"\n=== {changements} changement(s) enregistres. ===")