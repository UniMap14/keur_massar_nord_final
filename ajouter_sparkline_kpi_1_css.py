# -*- coding: utf-8 -*-
"""
Ajoute le CSS du mini-graphique de tendance (sparkline) affiche dans
la carte KPI "Recouvrement total".

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''    .kpi-card .label,
    .kpi-card .value,
    .kpi-card .delta {
        position: relative;
        z-index: 1;
        color: inherit;
    }'''

NOUVEAU = '''    .kpi-card .label,
    .kpi-card .value,
    .kpi-card .delta {
        position: relative;
        z-index: 1;
        color: inherit;
    }
    .kpi-sparkline {
        display: block;
        width: 100%;
        height: 30px;
        margin-top: 10px;
        position: relative;
        z-index: 1;
    }'''

if '.kpi-sparkline {' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre CSS introuvable (.kpi-card .label, .value, .delta)")
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