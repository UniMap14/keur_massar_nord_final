CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

remplacements = [
    ("@role_requis('technique')\ndef dashboard_parcelle_delete(request, pk):",
     "@role_requis('chef_technique')\ndef dashboard_parcelle_delete(request, pk):"),
    ("@role_requis('technique')\ndef dashboard_categorie_delete(request, pk):",
     "@role_requis('chef_technique')\ndef dashboard_categorie_delete(request, pk):"),
    ("@role_requis('technique')\ndef dashboard_infrastructure_delete(request, pk):",
     "@role_requis('chef_technique')\ndef dashboard_infrastructure_delete(request, pk):"),
    ("@role_requis('technique')\ndef dashboard_actualite_delete(request, pk):",
     "@role_requis('chef_technique')\ndef dashboard_actualite_delete(request, pk):"),
    ("@role_requis('fiscal')\ndef dashboard_declaration_traiter(request, pk):",
     "@role_requis('chef_fiscal')\ndef dashboard_declaration_traiter(request, pk):"),
    ("@role_requis('fiscal')\ndef dashboard_recours_traiter(request, pk):",
     "@role_requis('chef_fiscal')\ndef dashboard_recours_traiter(request, pk):"),
    ("@role_requis('fiscal')\ndef dashboard_immatriculation_traiter(request, pk):",
     "@role_requis('chef_fiscal')\ndef dashboard_immatriculation_traiter(request, pk):"),
    ("@role_requis('fiscal')\ndef dashboard_exoneration_traiter(request, pk):",
     "@role_requis('chef_fiscal')\ndef dashboard_exoneration_traiter(request, pk):"),
    ("@role_requis('fiscal')\ndef dashboard_plan_paiement_traiter(request, pk):",
     "@role_requis('chef_fiscal')\ndef dashboard_plan_paiement_traiter(request, pk):"),
    ("@role_requis('fiscal')\ndef dashboard_mutation_traiter(request, pk):",
     "@role_requis('chef_fiscal')\ndef dashboard_mutation_traiter(request, pk):"),
    ("@role_requis('fiscal')\ndef dashboard_paiement_valider(request, pk):",
     "@role_requis('chef_fiscal')\ndef dashboard_paiement_valider(request, pk):"),
    ("@staff_member_required(login_url='dashboard_login')\ndef dashboard_morcellement_fusion_traiter(request, pk):",
     "@staff_member_required(login_url='dashboard_login')\n@role_requis('chef_technique')\ndef dashboard_morcellement_fusion_traiter(request, pk):"),
]

resultats = []
for ancien, nouveau in remplacements:
    nom_fonction = ancien.split("def ")[1].split("(")[0]
    if nouveau in contenu:
        resultats.append(f"IGNORE : {nom_fonction} (deja a jour)")
    elif ancien in contenu:
        contenu = contenu.replace(ancien, nouveau, 1)
        resultats.append(f"OK : {nom_fonction}")
    else:
        resultats.append(f"ERREUR : {nom_fonction} introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))