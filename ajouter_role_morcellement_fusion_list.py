# -*- coding: utf-8 -*-
"""
Priorite 2 : dashboard_morcellement_fusion_list n'avait que
@staff_member_required(login_url='dashboard_login') (aucun controle de role),
alors que sa jumelle dashboard_morcellement_fusion_traiter exige deja
@role_requis('chef_technique'). N'importe quel agent connecte (meme du
service Fiscalite) pouvait donc consulter la liste des demandes de
morcellement/fusion. On aligne la liste sur le meme service que le
traitement : role 'technique' (ouvert au Chef ET au Gestionnaire Cadastre,
comme le reste des listes de validation : voir _list vs _traiter pour
Declaration/Recours/etc.).

Idempotent.
"""
CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''@staff_member_required(login_url='dashboard_login')
def dashboard_morcellement_fusion_list(request):'''

NOUVEAU = '''@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_morcellement_fusion_list(request):'''

if "@role_requis('technique')\ndef dashboard_morcellement_fusion_list(request):" in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (def dashboard_morcellement_fusion_list)")
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