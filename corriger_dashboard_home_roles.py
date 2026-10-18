# -*- coding: utf-8 -*-
"""
Priorite 3 : dashboard_home ne transmettait jamais peut_fiscal ni
peut_technique dans son contexte, alors que le template
dashboard/home.html les attend deja ({% if peut_fiscal %}, {% if peut_technique %})
pour afficher les KPI/graphiques/panneaux du bon service. Resultat actuel :
ces variables etant absentes du contexte, TOUS les blocs qui en dependent
(KPI recouvrement, contentieux fonciers, KPI parcelles cadastrees,
proprietaires, barre de recouvrement, graphiques, derniers paiements,
parcelles en retard) sont invisibles pour tout le monde, quel que soit
le role.

On ajoute les deux variables, calculees via a_role() (deja importe) :
  - peut_fiscal    -> a_role(request.user, 'fiscal')
  - peut_technique -> a_role(request.user, 'technique')
a_role() gere deja la retrocompatibilite (superviseur et compte staff
sans groupe assigne voient tout).

Idempotent.
"""
CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''    context = {
        "active_section": "home",
        "nb_parcelles": Parcelle.objects.count(),'''

NOUVEAU = '''    context = {
        "active_section": "home",
        "peut_fiscal": a_role(request.user, 'fiscal'),
        "peut_technique": a_role(request.user, 'technique'),
        "nb_parcelles": Parcelle.objects.count(),'''

if '"peut_fiscal": a_role(request.user' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (debut du dict context de dashboard_home)")
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