# -*- coding: utf-8 -*-
"""
Round 15 (home.html) : la 2e ligne de la grille KPI (Demandes en
cours / Infrastructures recensees / Messages non traites) ne comptait
que 3 cartes sur 6 colonnes, laissant 3 emplacements vides ("ligne
discontinue"). On elargit ces 3 cartes reelles (deja existantes, deja
cliquables, deja alimentees par de vraies donnees) pour qu'elles
occupent toute la largeur de la ligne, au lieu d'inventer un contenu
qui n'existe pas (photo, texte marketing).

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Carte "Demandes en cours"
# ---------------------------------------------------------------------
ANCRE_DEMANDES = """<a href="{% url 'dashboard_demande_list' %}" class="kpi-card tone-gold" style="text-decoration:none; color:inherit; display:block;">"""
AJOUT_DEMANDES = """<a href="{% url 'dashboard_demande_list' %}" class="kpi-card tone-gold kpi-span2" style="text-decoration:none; color:inherit; display:block;">"""
if 'kpi-card tone-gold kpi-span2" style="text-decoration:none; color:inherit; display:block;">\n    <div class="kpi-icon"><i class="fa-solid fa-folder-open">' in texte:
    pass
elif ANCRE_DEMANDES not in texte:
    erreurs.append("ANCRE_DEMANDES introuvable")
else:
    texte = texte.replace(ANCRE_DEMANDES, AJOUT_DEMANDES, 1)

# ---------------------------------------------------------------------
# 2) Carte "Infrastructures recensees"
# ---------------------------------------------------------------------
ANCRE_INFRA = """  <div class="kpi-card tone-blue">
    <div class="kpi-icon"><i class="fa-solid fa-road-bridge"></i></div>"""
AJOUT_INFRA = """  <div class="kpi-card tone-blue kpi-span2">
    <div class="kpi-icon"><i class="fa-solid fa-road-bridge"></i></div>"""
if 'kpi-card tone-blue kpi-span2">\n    <div class="kpi-icon"><i class="fa-solid fa-road-bridge">' in texte:
    pass
elif ANCRE_INFRA not in texte:
    erreurs.append("ANCRE_INFRA introuvable")
else:
    texte = texte.replace(ANCRE_INFRA, AJOUT_INFRA, 1)

# ---------------------------------------------------------------------
# 3) Carte "Messages non traites"
# ---------------------------------------------------------------------
ANCRE_MESSAGES = """<a href="{% url 'dashboard_message_list' %}" class="kpi-card tone-gold" style="text-decoration:none; color:inherit; display:block;">"""
AJOUT_MESSAGES = """<a href="{% url 'dashboard_message_list' %}" class="kpi-card tone-gold kpi-span2" style="text-decoration:none; color:inherit; display:block;">"""
if 'kpi-card tone-gold kpi-span2" style="text-decoration:none; color:inherit; display:block;">\n    <div class="kpi-icon"><i class="fa-solid fa-envelope-open-text">' in texte:
    pass
elif ANCRE_MESSAGES not in texte:
    erreurs.append("ANCRE_MESSAGES introuvable")
else:
    texte = texte.replace(ANCRE_MESSAGES, AJOUT_MESSAGES, 1)

# ---------------------------------------------------------------------
# 4) CSS : kpi-span2 occupe 2 colonnes (sur les 6 de la kpi-grid)
# ---------------------------------------------------------------------
ANCRE_CSS = """    .dashboard-grid .chart-legend-list li {
        font-size: 10.5px !important;
    }"""
AJOUT_CSS = """    .dashboard-grid .chart-legend-list li {
        font-size: 10.5px !important;
    }

    /* ===== Comble la 2e ligne de KPI incomplete (round 15) ===== */
    .kpi-grid .kpi-span2 {
        grid-column: span 2 !important;
    }
"""
if "Comble la 2e ligne de KPI incomplete (round 15)" in texte:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, AJOUT_CSS, 1)

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
    print("OK : dashboard/home.html -- round 15 (2e ligne KPI complete, sans inventer de contenu).")