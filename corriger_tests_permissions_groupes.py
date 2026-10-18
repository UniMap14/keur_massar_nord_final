# -*- coding: utf-8 -*-
"""
Les 5 groupes de roles sont deja crees par la migration de donnees
foncier.0020_creer_groupes_agents, y compris dans la base de test.
Group.objects.create(...) provoquait donc une IntegrityError (cle unique
'name' deja existante). On utilise get_or_create a la place.

Idempotent.
"""
CHEMIN = "foncier/tests_permissions.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''        cls.groupe_superviseur = Group.objects.create(name=GROUPE_SUPERVISEUR)
        cls.groupe_chef_technique = Group.objects.create(name=GROUPE_CHEF_TECHNIQUE)
        cls.groupe_gestionnaire_technique = Group.objects.create(name=GROUPE_GESTIONNAIRE_TECHNIQUE)
        cls.groupe_chef_fiscal = Group.objects.create(name=GROUPE_CHEF_FISCAL)
        cls.groupe_gestionnaire_fiscal = Group.objects.create(name=GROUPE_GESTIONNAIRE_FISCAL)'''

NOUVEAU = '''        cls.groupe_superviseur, _ = Group.objects.get_or_create(name=GROUPE_SUPERVISEUR)
        cls.groupe_chef_technique, _ = Group.objects.get_or_create(name=GROUPE_CHEF_TECHNIQUE)
        cls.groupe_gestionnaire_technique, _ = Group.objects.get_or_create(name=GROUPE_GESTIONNAIRE_TECHNIQUE)
        cls.groupe_chef_fiscal, _ = Group.objects.get_or_create(name=GROUPE_CHEF_FISCAL)
        cls.groupe_gestionnaire_fiscal, _ = Group.objects.get_or_create(name=GROUPE_GESTIONNAIRE_FISCAL)'''

if 'Group.objects.get_or_create(name=GROUPE_SUPERVISEUR)' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (creation des groupes dans setUpTestData)")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")