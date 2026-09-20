CHEMIN_VUE = "citoyens/views.py"
CHEMIN_TEMPLATE = "foncier/templates/foncier/fiscalite.html"

changements = 0

with open(CHEMIN_VUE, encoding="utf-8") as f:
    contenu_vue = f.read()

ancien_decorateur = "@login_required\ndef espace_personnel_view(request):"
nouveau_decorateur = "@login_required(login_url='citoyen_login')\ndef espace_personnel_view(request):"

if nouveau_decorateur in contenu_vue:
    print("DEJA FAIT : decorateur deja corrige.")
elif ancien_decorateur in contenu_vue:
    contenu_vue = contenu_vue.replace(ancien_decorateur, nouveau_decorateur, 1)
    with open(CHEMIN_VUE, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_vue)
    changements += 1
    print("OK : espace_personnel_view redirige maintenant vers la connexion citoyenne si non connecte.")
else:
    print("ERREUR : decorateur exact introuvable dans citoyens/views.py.")

with open(CHEMIN_TEMPLATE, encoding="utf-8") as f:
    contenu_template = f.read()

ancien_bouton = '''    <button class="tab-btn" data-tab="communal" role="tab" id="tab-communal" aria-selected="false" aria-controls="panel-communal">
      <i class="fa-solid fa-house-user"></i> Mon espace communal
    </button>'''

nouveau_bouton = '''    <a href="{% url 'citoyen_espace' %}" class="tab-btn" style="text-decoration:none;">
      <i class="fa-solid fa-house-user"></i> Mon espace communal
    </a>'''

if nouveau_bouton in contenu_template:
    print("DEJA FAIT : lien deja corrige.")
elif ancien_bouton in contenu_template:
    contenu_template = contenu_template.replace(ancien_bouton, nouveau_bouton, 1)
    with open(CHEMIN_TEMPLATE, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_template)
    changements += 1
    print("OK : 'Mon espace communal' est maintenant un vrai lien vers l'espace citoyen.")
else:
    print("ERREUR : bouton exact introuvable dans fiscalite.html.")

print(f"\n=== {changements} changement(s) enregistres. ===")