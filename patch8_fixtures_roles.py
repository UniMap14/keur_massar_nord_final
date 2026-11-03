CHEMIN = "foncier/tests/fixtures.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    if role:
        noms = {"fiscal": "Agent fiscal", "technique": "Agent technique", "superviseur": "Superviseur"}
        groupe, _ = Group.objects.get_or_create(name=noms[role])
        user.groups.add(groupe)
    return user'''

nouveau = '''    if role:
        from foncier.permissions import ROLE_VERS_GROUPE
        groupe, _ = Group.objects.get_or_create(name=ROLE_VERS_GROUPE[role])
        user.groups.add(groupe)
    return user'''

if ancien not in contenu:
    print("ECHEC : bloc attendu introuvable (verifie manuellement).")
else:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : fixtures.py utilise maintenant ROLE_VERS_GROUPE de permissions.py.")