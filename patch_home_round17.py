# -*- coding: utf-8 -*-
"""
Round 17 (home.html) : annule le round 16 -- retire les 3 cartes KPI
ajoutees (Signalements en cours, Inscriptions en attente, Projets
jeunes). Retour strict aux 9 cartes KPI de l'image de reference,
le tableau de bord etant juge trop charge avec 12 cartes.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE = """{% if peut_technique %}
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
AJOUT = """</div>

<div class="dashboard-grid">"""
if ANCRE in texte:
    texte = texte.replace(ANCRE, AJOUT, 1)
elif '<div class="label">Projets jeunes</div>' not in texte:
    pass  # deja retire
else:
    erreurs.append("ANCRE (bloc des 3 cartes) introuvable sous la forme exacte attendue")

if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : dashboard/home.html -- round 17 (retour a 9 cartes KPI).")