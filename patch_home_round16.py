# -*- coding: utf-8 -*-
"""
Round 16 (home.html) : annule l'elargissement (kpi-span2) des 3
cartes de la 2e ligne KPI (plus necessaire), et ajoute 3 nouvelles
cartes KPI reelles (Signalements en cours, Inscriptions en attente,
Projets jeunes) pour obtenir 6 cartes sur la ligne 2, comme la
ligne 1. Toutes basees sur des donnees et des URLs reelles
existantes, avec les memes permissions que dans la sidebar.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Annule le kpi-span2 (round 15) sur les 3 cartes existantes
# ---------------------------------------------------------------------
remplacements_retour = [
    ('class="kpi-card tone-gold kpi-span2" style="text-decoration:none; color:inherit; display:block;">\n    <div class="kpi-icon"><i class="fa-solid fa-folder-open">',
     'class="kpi-card tone-gold" style="text-decoration:none; color:inherit; display:block;">\n    <div class="kpi-icon"><i class="fa-solid fa-folder-open">'),
    ('class="kpi-card tone-blue kpi-span2">\n    <div class="kpi-icon"><i class="fa-solid fa-road-bridge">',
     'class="kpi-card tone-blue">\n    <div class="kpi-icon"><i class="fa-solid fa-road-bridge">'),
    ('class="kpi-card tone-gold kpi-span2" style="text-decoration:none; color:inherit; display:block;">\n    <div class="kpi-icon"><i class="fa-solid fa-envelope-open-text">',
     'class="kpi-card tone-gold" style="text-decoration:none; color:inherit; display:block;">\n    <div class="kpi-icon"><i class="fa-solid fa-envelope-open-text">'),
]
for ancienne, nouvelle in remplacements_retour:
    if ancienne in texte:
        texte = texte.replace(ancienne, nouvelle, 1)

# ---------------------------------------------------------------------
# 2) Ajoute 3 nouvelles cartes KPI reelles, juste avant la fermeture
#    de kpi-grid (identifiee par la transition ASCII vers dashboard-grid)
# ---------------------------------------------------------------------
ANCRE = """</div>

<div class="dashboard-grid">"""
AJOUT = """{% if peut_technique %}
  <a href="{% url 'dashboard_signalement_list' %}" class="kpi-card tone-red" style="text-decoration:none; color:inherit; display:block;">
    <div class="kpi-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>
    <span class="kpi-corner-icon"><i class="fa-solid fa-triangle-exclamation"></i></span>
    <div class="label">Signalements en cours</div>
    <div class="value">{{ nb_signalements_en_cours|default:0 }}</div>
    <div class="delta">Signales par des citoyens</div>
  </a>
{% endif %}
  <a href="{% url 'gestion_inscriptions' %}" class="kpi-card tone-green" style="text-decoration:none; color:inherit; display:block;">
    <div class="kpi-icon"><i class="fa-solid fa-user-check"></i></div>
    <span class="kpi-corner-icon"><i class="fa-solid fa-user-check"></i></span>
    <div class="label">Inscriptions en attente</div>
    <div class="value">{{ nb_inscriptions_en_attente|default:0 }}</div>
    <div class="delta">Comptes citoyens a valider</div>
  </a>
  <a href="{% url 'dashboard_jeunesse_list' %}" class="kpi-card tone-purple" style="text-decoration:none; color:inherit; display:block;">
    <div class="kpi-icon"><i class="fa-solid fa-seedling"></i></div>
    <span class="kpi-corner-icon"><i class="fa-solid fa-seedling"></i></span>
    <div class="label">Projets jeunes</div>
    <div class="value">{{ nb_projets_jeunes|default:0 }}</div>
    <div class="delta">Deposes par des jeunes</div>
  </a>
</div>

<div class="dashboard-grid">"""
if '<div class="label">Projets jeunes</div>' in texte:
    pass
elif ANCRE not in texte:
    erreurs.append("ANCRE introuvable")
else:
    texte = texte.replace(ANCRE, AJOUT, 1)

# ---------------------------------------------------------------------
if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard/home.html -- round 16 (6 cartes reelles sur la 2e ligne KPI).")