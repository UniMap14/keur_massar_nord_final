CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService"
nouveau = "from foncier.models import Parcelle, ProfilCitoyen, DemandeService, DeclarationFiscale"

if nouveau in contenu:
    print("DEJA FAIT : import deja correct.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : import DeclarationFiscale vraiment ajoute cette fois.")
else:
    print("ERREUR : ligne d'import introuvable.")