CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_choices = '''    ROLE_CHOICES = [
        ("", "Aucun rôle spécifique (accès complet, compte historique)"),
        ("superviseur", "Superviseur (accès à tout)"),
        ("fiscal", "Agent fiscal (contribuables, taxations, paiements)"),
        ("technique", "Agent technique (parcelles, infrastructures, signalements)"),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=False, label="Rôle")'''

nouveau_choices = '''    ROLE_CHOICES = [
        ("", "Aucun rôle spécifique (accès complet, compte historique)"),
        ("superviseur", "Superviseur (accès à tout — Maire)"),
        ("chef_technique", "Chef du Service Cadastre (validation, suppression, signature)"),
        ("technique", "Gestionnaire Cadastre (parcelles, infrastructures, opérations courantes)"),
        ("chef_fiscal", "Chef du Service Fiscalité (validation, suppression, signature)"),
        ("fiscal", "Gestionnaire Fiscalité (contribuables, taxations, paiements, opérations courantes)"),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=False, label="Rôle")'''

if nouveau_choices in contenu:
    resultats.append("IGNORE : ROLE_CHOICES (deja a jour)")
elif ancien_choices in contenu:
    contenu = contenu.replace(ancien_choices, nouveau_choices, 1)
    resultats.append("OK : ROLE_CHOICES etendu a 5 choix")
else:
    resultats.append("ERREUR : ROLE_CHOICES introuvable")

ancien_detect = '''    agent = get_object_or_404(User, pk=pk, is_staff=True)
    noms_groupes_roles = {GROUPE_SUPERVISEUR, GROUPE_FISCAL, GROUPE_TECHNIQUE}
    role_actuel = ""
    for nom, cle in [(GROUPE_SUPERVISEUR, "superviseur"), (GROUPE_FISCAL, "fiscal"), (GROUPE_TECHNIQUE, "technique")]:
        if agent.groups.filter(name=nom).exists():
            role_actuel = cle
            break'''

nouveau_detect = '''    agent = get_object_or_404(User, pk=pk, is_staff=True)
    noms_groupes_roles = {
        GROUPE_SUPERVISEUR, GROUPE_CHEF_TECHNIQUE, GROUPE_GESTIONNAIRE_TECHNIQUE,
        GROUPE_CHEF_FISCAL, GROUPE_GESTIONNAIRE_FISCAL,
    }
    role_actuel = ""
    for nom, cle in [
        (GROUPE_SUPERVISEUR, "superviseur"),
        (GROUPE_CHEF_TECHNIQUE, "chef_technique"),
        (GROUPE_GESTIONNAIRE_TECHNIQUE, "technique"),
        (GROUPE_CHEF_FISCAL, "chef_fiscal"),
        (GROUPE_GESTIONNAIRE_FISCAL, "fiscal"),
    ]:
        if agent.groups.filter(name=nom).exists():
            role_actuel = cle
            break'''

if nouveau_detect in contenu:
    resultats.append("IGNORE : detection du role actuel (deja a jour)")
elif ancien_detect in contenu:
    contenu = contenu.replace(ancien_detect, nouveau_detect, 1)
    resultats.append("OK : detection du role actuel etendue a 5 groupes")
else:
    resultats.append("ERREUR : bloc de detection introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))