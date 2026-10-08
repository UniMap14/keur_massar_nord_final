CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "{% extends 'dashboard/base.html' %}"
nouveau = "{% extends 'dashboard/geoportail_shell.html' %}"

if nouveau in contenu:
    print("DEJA FAIT : extends deja mis a jour.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : geoportail_admin.html utilise maintenant le gabarit plein ecran.")
else:
    print("ERREUR : ligne exacte introuvable.")