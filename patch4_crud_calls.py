CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

remplacements = [
    (
        '''dashboard_proprietaire_create, dashboard_proprietaire_update, dashboard_proprietaire_delete = _crud_views(
    Propriétaire, ProprietaireForm, "dashboard_proprietaire_list", "Propriétaire", roles=('technique',)
)''',
        '''dashboard_proprietaire_create, dashboard_proprietaire_update, dashboard_proprietaire_delete = _crud_views(
    Propriétaire, ProprietaireForm, "dashboard_proprietaire_list", "Propriétaire",
    roles=('technique',), roles_delete=('chef_technique',),
)''',
    ),
    (
        '''_, dashboard_zone_update, dashboard_zone_delete = _crud_views(
    Zone, ZoneRenameForm, "dashboard_zone_list", "Zone", roles=('technique',)
)''',
        '''_, dashboard_zone_update, dashboard_zone_delete = _crud_views(
    Zone, ZoneRenameForm, "dashboard_zone_list", "Zone",
    roles=('technique',), roles_delete=('chef_technique',),
)''',
    ),
    (
        '''dashboard_contribuable_create, dashboard_contribuable_update, dashboard_contribuable_delete = _crud_views(
    Contribuable, ContribuableForm, "dashboard_contribuable_list", "Contribuable", roles=('fiscal',)
)''',
        '''dashboard_contribuable_create, dashboard_contribuable_update, dashboard_contribuable_delete = _crud_views(
    Contribuable, ContribuableForm, "dashboard_contribuable_list", "Contribuable",
    roles=('fiscal',), roles_delete=('chef_fiscal',),
)''',
    ),
    (
        '''dashboard_typetaxe_create, dashboard_typetaxe_update, dashboard_typetaxe_delete = _crud_views(
    TypeTaxe, TypeTaxeForm, "dashboard_typetaxe_list", "Type de taxe", roles=('fiscal',)
)''',
        '''dashboard_typetaxe_create, dashboard_typetaxe_update, dashboard_typetaxe_delete = _crud_views(
    TypeTaxe, TypeTaxeForm, "dashboard_typetaxe_list", "Type de taxe",
    roles=('fiscal',), roles_delete=('chef_fiscal',),
)''',
    ),
    (
        '''dashboard_taxation_create, dashboard_taxation_update, dashboard_taxation_delete = _crud_views(
    Taxation, TaxationForm, "dashboard_taxation_list", "Taxation", roles=('fiscal',)
)''',
        '''dashboard_taxation_create, dashboard_taxation_update, dashboard_taxation_delete = _crud_views(
    Taxation, TaxationForm, "dashboard_taxation_list", "Taxation",
    roles=('fiscal',), roles_delete=('chef_fiscal',),
)''',
    ),
    (
        '''dashboard_paiement_create, dashboard_paiement_update, dashboard_paiement_delete = _crud_views(
    Paiement, PaiementForm, "dashboard_paiement_list", "Paiement", roles=('fiscal',)
)''',
        '''dashboard_paiement_create, dashboard_paiement_update, dashboard_paiement_delete = _crud_views(
    Paiement, PaiementForm, "dashboard_paiement_list", "Paiement",
    roles=('fiscal',), roles_delete=('chef_fiscal',),
)''',
    ),
    (
        '''dashboard_profil_create, dashboard_profil_update, dashboard_profil_delete = _crud_views(
    ProfilCitoyen, ProfilCitoyenForm, "dashboard_profil_list", "Profil citoyen", roles=('fiscal',)
)''',
        '''dashboard_profil_create, dashboard_profil_update, dashboard_profil_delete = _crud_views(
    ProfilCitoyen, ProfilCitoyenForm, "dashboard_profil_list", "Profil citoyen",
    roles=('fiscal',), roles_delete=('chef_fiscal',),
)''',
    ),
]

resultats = []
for ancien, nouveau in remplacements:
    nom = ancien.split(",")[0].strip()
    if nouveau in contenu:
        resultats.append(f"IGNORE : {nom} (deja a jour)")
    elif ancien in contenu:
        contenu = contenu.replace(ancien, nouveau, 1)
        resultats.append(f"OK : {nom}")
    else:
        resultats.append(f"ERREUR : {nom} introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))