CHEMIN = "foncier/paiement_gateway.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''def get_backend(nom=None):
    nom = nom or getattr(settings, "PAIEMENT_BACKEND", "manuel")
    return BACKENDS.get(nom, ManuelBackend)()'''

nouveau = '''def get_backend(nom=None):
    backend_global = getattr(settings, "PAIEMENT_BACKEND", "manuel")
    if backend_global == "manuel":
        # Mode demo : simule TOUJOURS un paiement confirme, quel que soit
        # l'operateur choisi par le citoyen (Orange Money/Wave), pour ne
        # jamais exiger de vraies cles API tant que le projet est en
        # developpement/demonstration.
        return ManuelBackend()
    nom = nom or backend_global
    return BACKENDS.get(nom, ManuelBackend)()'''

if "Mode demo : simule TOUJOURS" in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : le mode manuel s'applique maintenant quel que soit l'operateur choisi.")
else:
    print("ERREUR : bloc exact introuvable.")