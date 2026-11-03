# -*- coding: utf-8 -*-
"""
Remplace la barre de recherche du topbar (dashboard/base.html) : au
lieu de rediriger systematiquement vers la liste des parcelles et de
n'etre visible que pour le role "technique", elle pointe maintenant
vers la recherche globale intelligente (parcelles + proprietaires +
contribuables selon le role), visible par tout agent connecte, avec un
vrai bouton.

Idempotent.
"""
import io

chemin = "foncier/templates/dashboard/base.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

if "dashboard_recherche_globale" in contenu:
    print("Deja applique, rien a faire.")
else:
    ancien = '''      {% if peut_technique %}
      <form method="get" action="{% url 'dashboard_parcelle_list' %}" class="topbar-search">
        <input type="text" name="q" placeholder="Rechercher une parcelle, un proprietaire...">
      </form>
      {% endif %}'''

    if ancien not in contenu:
        raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie. Le fichier a peut-etre ete modifie entre temps.")

    nouveau = '''      <form method="get" action="{% url 'dashboard_recherche_globale' %}" class="topbar-search">
        <input type="text" name="q" placeholder="Rechercher parcelle, proprietaire, contribuable...">
        <button type="submit" aria-label="Rechercher"><i class="fa-solid fa-magnifying-glass"></i></button>
      </form>'''

    contenu = contenu.replace(ancien, nouveau)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")