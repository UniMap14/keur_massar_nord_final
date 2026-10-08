CHEMIN_PERM = "foncier/permissions.py"
CHEMIN_VIEWS = "foncier/dashboard_views.py"

resultats = []

# ============================================================
# 1. permissions.py : ajout de 2 roles "gestionnaire seul"
# ============================================================
with open(CHEMIN_PERM, encoding="utf-8") as f:
    perm = f.read()

ancien_dict = '''ROLE_VERS_GROUPES = {
    "superviseur": {GROUPE_SUPERVISEUR},
    "technique": GROUPES_SERVICE_TECHNIQUE,
    "fiscal": GROUPES_SERVICE_FISCAL,
    "chef_technique": GROUPES_CHEF_TECHNIQUE,
    "chef_fiscal": GROUPES_CHEF_FISCAL,
}'''

nouveau_dict = '''ROLE_VERS_GROUPES = {
    "superviseur": {GROUPE_SUPERVISEUR},
    "technique": GROUPES_SERVICE_TECHNIQUE,
    "fiscal": GROUPES_SERVICE_FISCAL,
    "chef_technique": GROUPES_CHEF_TECHNIQUE,
    "chef_fiscal": GROUPES_CHEF_FISCAL,
    # Reserve au Gestionnaire SEUL (le Chef ne cree pas de nouvelles entrees,
    # il valide/modifie/supprime ce que le Gestionnaire a saisi).
    "gestionnaire_technique": {GROUPE_GESTIONNAIRE_TECHNIQUE},
    "gestionnaire_fiscal": {GROUPE_GESTIONNAIRE_FISCAL},
}'''

if '"gestionnaire_technique"' in perm:
    resultats.append("permissions.py : IGNORE (deja present)")
elif ancien_dict in perm:
    perm = perm.replace(ancien_dict, nouveau_dict, 1)
    with open(CHEMIN_PERM, "w", encoding="utf-8", newline="") as f:
        f.write(perm)
    resultats.append("permissions.py : OK (2 roles gestionnaire-seul ajoutes)")
else:
    resultats.append("permissions.py : ERREUR bloc introuvable")

# ============================================================
# 2. dashboard_views.py : _crud_views accepte roles_create
# ============================================================
with open(CHEMIN_VIEWS, encoding="utf-8") as f:
    views = f.read()

ancien_sig = '''def _crud_views(model, form_class, list_url_name, titre, str_field="pk", roles=(), roles_delete=None):'''
nouveau_sig = '''def _crud_views(model, form_class, list_url_name, titre, str_field="pk", roles=(), roles_delete=None, roles_create=None):'''

if "roles_create=None" in views:
    resultats.append("_crud_views signature : IGNORE (deja present)")
elif ancien_sig in views:
    views = views.replace(ancien_sig, nouveau_sig, 1)
    resultats.append("_crud_views signature : OK")
else:
    resultats.append("_crud_views signature : ERREUR introuvable")

ancien_corps = '''    if roles:
        create_view = role_requis(*roles)(create_view)
        update_view = role_requis(*roles)(update_view)
    roles_suppression = roles_delete if roles_delete else roles
    if roles_suppression:
        delete_view = role_requis(*roles_suppression)(delete_view)

    return create_view, update_view, delete_view'''

nouveau_corps = '''    if roles:
        update_view = role_requis(*roles)(update_view)
    roles_creation = roles_create if roles_create else roles
    if roles_creation:
        create_view = role_requis(*roles_creation)(create_view)
    roles_suppression = roles_delete if roles_delete else roles
    if roles_suppression:
        delete_view = role_requis(*roles_suppression)(delete_view)

    return create_view, update_view, delete_view'''

if "roles_creation = roles_create" in views:
    resultats.append("_crud_views corps : IGNORE (deja present)")
elif ancien_corps in views:
    views = views.replace(ancien_corps, nouveau_corps, 1)
    resultats.append("_crud_views corps : OK")
else:
    resultats.append("_crud_views corps : ERREUR introuvable")

# ============================================================
# 3. Les 7 appels _crud_views() : ajout de roles_create
# ============================================================
appels = [
    ("Propriétaire, ProprietaireForm, \"dashboard_proprietaire_list\", \"Propriétaire\",\n    roles=('technique',), roles_delete=('chef_technique',),\n)",
     "Propriétaire, ProprietaireForm, \"dashboard_proprietaire_list\", \"Propriétaire\",\n    roles=('technique',), roles_delete=('chef_technique',), roles_create=('gestionnaire_technique',),\n)"),
    ("Zone, ZoneRenameForm, \"dashboard_zone_list\", \"Zone\",\n    roles=('technique',), roles_delete=('chef_technique',),\n)",
     "Zone, ZoneRenameForm, \"dashboard_zone_list\", \"Zone\",\n    roles=('technique',), roles_delete=('chef_technique',), roles_create=('gestionnaire_technique',),\n)"),
    ("Contribuable, ContribuableForm, \"dashboard_contribuable_list\", \"Contribuable\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',),\n)",
     "Contribuable, ContribuableForm, \"dashboard_contribuable_list\", \"Contribuable\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',), roles_create=('gestionnaire_fiscal',),\n)"),
    ("TypeTaxe, TypeTaxeForm, \"dashboard_typetaxe_list\", \"Type de taxe\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',),\n)",
     "TypeTaxe, TypeTaxeForm, \"dashboard_typetaxe_list\", \"Type de taxe\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',), roles_create=('gestionnaire_fiscal',),\n)"),
    ("Taxation, TaxationForm, \"dashboard_taxation_list\", \"Taxation\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',),\n)",
     "Taxation, TaxationForm, \"dashboard_taxation_list\", \"Taxation\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',), roles_create=('gestionnaire_fiscal',),\n)"),
    ("Paiement, PaiementForm, \"dashboard_paiement_list\", \"Paiement\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',),\n)",
     "Paiement, PaiementForm, \"dashboard_paiement_list\", \"Paiement\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',), roles_create=('gestionnaire_fiscal',),\n)"),
    ("ProfilCitoyen, ProfilCitoyenForm, \"dashboard_profil_list\", \"Profil citoyen\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',),\n)",
     "ProfilCitoyen, ProfilCitoyenForm, \"dashboard_profil_list\", \"Profil citoyen\",\n    roles=('fiscal',), roles_delete=('chef_fiscal',), roles_create=('gestionnaire_fiscal',),\n)"),
]

for ancien, nouveau in appels:
    nom = ancien.split(",")[0].strip()
    if "roles_create=('gestionnaire_" in nouveau and nouveau in views:
        resultats.append(f"appel {nom} : IGNORE (deja present)")
    elif ancien in views:
        views = views.replace(ancien, nouveau, 1)
        resultats.append(f"appel {nom} : OK")
    else:
        resultats.append(f"appel {nom} : ERREUR introuvable")

# ============================================================
# 4. Les 4 vues create individuelles : technique -> gestionnaire_technique
# ============================================================
individuelles = [
    ("@role_requis('technique')\ndef dashboard_parcelle_create(request):",
     "@role_requis('gestionnaire_technique')\ndef dashboard_parcelle_create(request):"),
    ("@role_requis('technique')\ndef dashboard_categorie_create(request):",
     "@role_requis('gestionnaire_technique')\ndef dashboard_categorie_create(request):"),
    ("@role_requis('technique')\ndef dashboard_infrastructure_create(request):",
     "@role_requis('gestionnaire_technique')\ndef dashboard_infrastructure_create(request):"),
    ("@role_requis('technique')\ndef dashboard_actualite_create(request):",
     "@role_requis('gestionnaire_technique')\ndef dashboard_actualite_create(request):"),
]

for ancien, nouveau in individuelles:
    nom_fonction = ancien.split("def ")[1].split("(")[0]
    if nouveau in views:
        resultats.append(f"{nom_fonction} : IGNORE (deja present)")
    elif ancien in views:
        views = views.replace(ancien, nouveau, 1)
        resultats.append(f"{nom_fonction} : OK")
    else:
        resultats.append(f"{nom_fonction} : ERREUR introuvable")

with open(CHEMIN_VIEWS, "w", encoding="utf-8", newline="") as f:
    f.write(views)

print("\n".join(resultats))