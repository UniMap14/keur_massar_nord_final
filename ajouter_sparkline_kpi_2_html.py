# -*- coding: utf-8 -*-
"""
Ajoute le canvas du mini-graphique dans la carte KPI "Recouvrement total".

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''  <div class="kpi-card tone-green">
    <div class="kpi-icon"><i class="fa-solid fa-sack-dollar"></i></div>
    <div class="label">Recouvrement total</div>
    <div class="value">{{ total_recouvre_fmt }}</div>
    <div class="delta">Total des taxes collectées</div>
  </div>'''

NOUVEAU = '''  <div class="kpi-card tone-green">
    <div class="kpi-icon"><i class="fa-solid fa-sack-dollar"></i></div>
    <div class="label">Recouvrement total</div>
    <div class="value">{{ total_recouvre_fmt }}</div>
    <div class="delta">Total des taxes collectées</div>
    <canvas id="kpiSparkRecouvrement" class="kpi-sparkline" height="30"></canvas>
  </div>'''

if 'id="kpiSparkRecouvrement"' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre HTML introuvable (carte KPI Recouvrement total)")
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