CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''def dashboard_journal_audit_list(request):
    if not _est_superviseur(request.user):
        raise PermissionDenied("Seuls les superviseurs peuvent consulter le journal d'audit.")'''

nouveau = '''def dashboard_journal_audit_list(request):
    if not (_est_superviseur(request.user) or a_role(request.user, 'chef_technique', 'chef_fiscal')):
        raise PermissionDenied("Seuls le Maire et les chefs de service peuvent consulter le journal d'audit.")'''

if ancien not in contenu:
    print("DEJA FAIT ou introuvable (verifie manuellement si besoin).")
else:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : acces au journal d'audit elargi aux chefs de service.")