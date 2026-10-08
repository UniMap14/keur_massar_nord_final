CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "from .permissions import role_requis, a_role, libelle_role\nfrom .permissions import GROUPE_SUPERVISEUR, GROUPE_FISCAL, GROUPE_TECHNIQUE, ROLE_VERS_GROUPE"
nouveau = ("from .permissions import role_requis, a_role, libelle_role\n"
           "from .permissions import (\n"
           "    GROUPE_SUPERVISEUR, GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE,\n"
           "    GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL, ROLE_VERS_GROUPE,\n"
           ")")

if "GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE," in contenu:
    print("DEJA FAIT : import deja mis a jour.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : import des groupes mis a jour.")
else:
    print("ERREUR : ligne exacte introuvable.")