CHEMIN = "foncier/context_processors.py"

AJOUT = '''

def profil_agent_connecte(request):
    """
    Ajoute 'mon_profil_agent' au contexte de tous les templates. Vaut
    absent si l'utilisateur n'est pas connecte ou n'est pas un agent
    (is_staff) -- jamais d'erreur, juste absence de profil affiche.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    from foncier.models import ProfilAgent

    profil, _ = ProfilAgent.objects.get_or_create(user=request.user)
    return {"mon_profil_agent": profil}
'''

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "def profil_agent_connecte" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : fonction profil_agent_connecte ajoutee a la fin du fichier existant.")