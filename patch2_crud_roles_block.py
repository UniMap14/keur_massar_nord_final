CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    if roles:
        create_view = role_requis(*roles)(create_view)
        update_view = role_requis(*roles)(update_view)
        delete_view = role_requis(*roles)(delete_view)

    return create_view, update_view, delete_view'''

nouveau = '''    if roles:
        create_view = role_requis(*roles)(create_view)
        update_view = role_requis(*roles)(update_view)
    roles_suppression = roles_delete if roles_delete else roles
    if roles_suppression:
        delete_view = role_requis(*roles_suppression)(delete_view)

    return create_view, update_view, delete_view'''

if "roles_suppression = roles_delete" in contenu:
    print("DEJA FAIT : bloc deja mis a jour.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : bloc roles/delete de _crud_views mis a jour.")
else:
    print("ERREUR : bloc exact introuvable.")