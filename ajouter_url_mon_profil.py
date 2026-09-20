Q = chr(34)
NL = chr(10)

CHEMIN = "foncier/dashboard_urls.py"
ANCRE = 'path("agents/", views.dashboard_agent_list, name="dashboard_agent_list"),'
AJOUT = NL + '    path("mon-profil/", views.dashboard_mon_profil, name="dashboard_mon_profil"),'

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "dashboard_mon_profil" in contenu:
    print("DEJA PRESENT : rien a faire.")
elif ANCRE not in contenu:
    print("ERREUR : ancre introuvable, rien modifie.")
else:
    contenu = contenu.replace(ANCRE, ANCRE + AJOUT, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : URL mon-profil ajoutee.")
