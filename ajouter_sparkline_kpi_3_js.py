# -*- coding: utf-8 -*-
"""
Initialise le mini-graphique Chart.js de la carte "Recouvrement total",
en reutilisant les donnees deja calculees (paiements des 12 derniers
mois) : aucune nouvelle requete, aucune donnee inventee.

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''    var palette = ['#2f7a4f', '#c9982e', '#3a7d44', '#b3261e', '#6f6a5e', '#8a8276', '#a3791f', '#7a7266'];

    var elEvolution = document.getElementById('chartEvolution');'''

NOUVEAU = '''    var palette = ['#2f7a4f', '#c9982e', '#3a7d44', '#b3261e', '#6f6a5e', '#8a8276', '#a3791f', '#7a7266'];

    var elSparkRecouvrement = document.getElementById('kpiSparkRecouvrement');
    if (elSparkRecouvrement) {
        new Chart(elSparkRecouvrement, {
            type: 'line',
            data: {
                labels: {{ chart_mois_labels|safe }},
                datasets: [{
                    data: {{ chart_mois_valeurs|safe }},
                    borderColor: '#3a7d44',
                    backgroundColor: 'rgba(58,125,68,0.12)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.35,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } },
            }
        });
    }

    var elEvolution = document.getElementById('chartEvolution');'''

if "kpiSparkRecouvrement" in contenu and "new Chart(elSparkRecouvrement" in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre JS introuvable (palette / elEvolution)")
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