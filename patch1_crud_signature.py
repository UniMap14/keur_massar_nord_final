CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = 'def _crud_views(model, form_class, list_url_name, titre, str_field="pk", roles=()):'
nouveau = 'def _crud_views(model, form_class, list_url_name, titre, str_field="pk", roles=(), roles_delete=None):'

if "roles_delete=None" in contenu:
    print("DEJA FAIT : signature deja mise a jour.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : signature de _crud_views mise a jour.")
else:
    print("ERREUR : ligne exacte introuvable.")