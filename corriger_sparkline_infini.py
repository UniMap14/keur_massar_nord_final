# -*- coding: utf-8 -*-
"""
Corrige le bug de boucle de redimensionnement infinie du mini-graphique
Chart.js "Recouvrement total" : le canvas responsive sans conteneur a
hauteur fixe grandissait sans fin (page qui defile a l'infini). On
enveloppe le canvas dans un conteneur a hauteur fixe, ce qui est le
correctif standard pour Chart.js en mode responsive.

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# 1) CSS : deplacer la hauteur fixe sur un conteneur dedie
ANCIEN_CSS = '''    .kpi-sparkline {
        display: block;
        width: 100%;
        height: 30px;
        margin-top: 10px;
        position: relative;
        z-index: 1;
    }'''

NOUVEAU_CSS = '''    .kpi-sparkline-wrap {
        position: relative;
        width: 100%;
        height: 30px;
        margin-top: 10px;
        z-index: 1;
        overflow: hidden;
    }
    .kpi-sparkline-wrap canvas {
        position: absolute;
        inset: 0;
        width: 100% !important;
        height: 100% !important;
    }'''

if '.kpi-sparkline-wrap {' in contenu:
    pass
elif ANCIEN_CSS not in contenu:
    erreurs.append("ancre CSS introuvable (.kpi-sparkline)")
else:
    contenu = contenu.replace(ANCIEN_CSS, NOUVEAU_CSS, 1)
    remplacements_ok += 1

# 2) HTML : envelopper le canvas dans le nouveau conteneur
ANCIEN_HTML = '''    <canvas id="kpiSparkRecouvrement" class="kpi-sparkline" height="30"></canvas>'''

NOUVEAU_HTML = '''    <div class="kpi-sparkline-wrap"><canvas id="kpiSparkRecouvrement"></canvas></div>'''

if 'class="kpi-sparkline-wrap"' in contenu:
    pass
elif ANCIEN_HTML not in contenu:
    erreurs.append("ancre HTML introuvable (canvas kpiSparkRecouvrement)")
else:
    contenu = contenu.replace(ANCIEN_HTML, NOUVEAU_HTML, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")