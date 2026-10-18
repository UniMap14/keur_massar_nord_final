# -*- coding: utf-8 -*-
"""
Round 19 (home.html) : supprime 3 panneaux du tableau de bord --
"Taux de recouvrement par zone", "Dernieres demandes", "Parcelle
recente" -- pour desencombrer, suite au retour "tableau de bord trop
charge". Les 9 panneaux de contenu restants sont reorganises sur
3 lignes de 6 colonnes sans espace vide.

Les donnees/requetes correspondantes restent dans dashboard_views.py
(aucun risque a les laisser, elles ne sont simplement plus affichees) ;
dites-moi si vous voulez aussi que je les retire du backend.

Idempotent. Ancres 100% ASCII (regex bornee pour le bloc "zones" qui
contient du texte accentue).
"""
import pathlib
import re

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) Supprime le panneau "Taux de recouvrement par zone" (regex bornee,
#    car son texte contient des caracteres accentues)
# ---------------------------------------------------------------------
DEBUT_ZONES = '  <div class="panel cell-zones">'
FIN_ZONES = '  <div class="panel cell-taxes">'
if DEBUT_ZONES not in texte:
    pass  # deja retire
elif FIN_ZONES not in texte:
    erreurs.append("FIN_ZONES (cell-taxes) introuvable -- impossible de borner la suppression")
else:
    motif = re.escape(DEBUT_ZONES) + r".*?(?=" + re.escape(FIN_ZONES) + r")"
    nouveau_texte, nb = re.subn(motif, "", texte, count=1, flags=re.S)
    if nb == 1:
        texte = nouveau_texte
    else:
        erreurs.append("regex cell-zones : aucune correspondance")

# ---------------------------------------------------------------------
# 2) Supprime le panneau "Dernieres demandes" (ASCII, suppression directe)
# ---------------------------------------------------------------------
BLOC_DEMANDES = """<div class="panel cell-demandes">
  <div class="panel-header">
    <h2><i class="fa-solid fa-folder-open"></i> Dernieres demandes</h2>
    <a href="{% url 'dashboard_demande_list' %}" class="btn btn-outline btn-sm">Voir tout</a>
  </div>
  <div class="panel-body flush">
    {% if dernieres_demandes %}
    <table class="data-table">
      <thead>
        <tr>
          <th>Reference</th>
          <th>Demandeur</th>
          <th>Date</th>
          <th>Statut</th>
        </tr>
      </thead>
      <tbody>
        {% for d in dernieres_demandes %}
        <tr>
          <td>{{ d.numero_dossier }}</td>
          <td>{{ d.demandeur.get_full_name|default:d.demandeur.username }}</td>
          <td>{{ d.date_demande|date:"d/m/Y" }}</td>
          <td>{{ d.get_statut_display }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div class="empty-state">
      <div class="icon icon-neutral"><i class="fa-regular fa-circle"></i></div>
      Aucune demande enregistree pour le moment.
    </div>
    {% endif %}
  </div>
</div>

"""
if BLOC_DEMANDES in texte:
    texte = texte.replace(BLOC_DEMANDES, "", 1)
elif '<h2><i class="fa-solid fa-folder-open"></i> Dernieres demandes</h2>' not in texte:
    pass  # deja retire
else:
    erreurs.append("BLOC_DEMANDES introuvable sous la forme exacte attendue")

# ---------------------------------------------------------------------
# 3) Supprime le panneau "Parcelle recente" (ASCII, suppression directe)
# ---------------------------------------------------------------------
BLOC_PARCELLE = """<div class="panel cell-parcelle-recente">
  <div class="panel-header">
    <h2><i class="fa-solid fa-map-pin"></i> Parcelle recente</h2>
    {% if parcelle_recente %}<a href="{% url 'dashboard_parcelle_update' parcelle_recente.pk %}" class="btn btn-outline btn-sm">Voir</a>{% endif %}
  </div>
  <div class="panel-body flush">
    {% if parcelle_recente %}
    <table class="data-table">
      <tbody>
        <tr><th>NICAD</th><td>{{ parcelle_recente.nicad }}</td></tr>
        <tr><th>Proprietaire</th><td>{% if parcelle_recente.proprietaire %}{{ parcelle_recente.proprietaire }}{% else %}<span style="color:var(--ink-quiet, #7a7266);">&mdash;</span>{% endif %}</td></tr>
        <tr><th>Superficie</th><td>{{ parcelle_recente.superficie|floatformat:0 }} m2</td></tr>
      </tbody>
    </table>
    {% else %}
    <div class="empty-state">
      <div class="icon icon-neutral"><i class="fa-regular fa-circle"></i></div>
      Aucune parcelle enregistree pour le moment.
    </div>
    {% endif %}
  </div>
</div>

"""
if BLOC_PARCELLE in texte:
    texte = texte.replace(BLOC_PARCELLE, "", 1)
elif '<h2><i class="fa-solid fa-map-pin"></i> Parcelle recente</h2>' not in texte:
    pass  # deja retire
else:
    erreurs.append("BLOC_PARCELLE introuvable sous la forme exacte attendue")

# ---------------------------------------------------------------------
# 4) Reorganise les 9 panneaux restants sur 3 lignes pleines de 6 colonnes
# ---------------------------------------------------------------------
ANCRE_CSS = """    .dashboard-grid .cell-paiements       { grid-column: span 2 !important; order: 6  !important; }
    .dashboard-grid .cell-retardataires   { grid-column: span 2 !important; order: 7  !important; }
    .dashboard-grid .cell-zones           { grid-column: span 2 !important; order: 8  !important; }
    .dashboard-grid .cell-quick-actions   { grid-column: span 2 !important; order: 9  !important; }
    .dashboard-grid .cell-demandes        { grid-column: span 2 !important; order: 10 !important; }
    .dashboard-grid .cell-parcelle-recente{ grid-column: span 1 !important; order: 11 !important; }
    .dashboard-grid .cell-activite        { grid-column: span 1 !important; order: 12 !important; }"""
AJOUT_CSS = """    .dashboard-grid .cell-paiements       { grid-column: span 3 !important; order: 6 !important; }
    .dashboard-grid .cell-retardataires   { grid-column: span 3 !important; order: 7 !important; }
    .dashboard-grid .cell-quick-actions   { grid-column: span 3 !important; order: 8 !important; }
    .dashboard-grid .cell-activite        { grid-column: span 3 !important; order: 9 !important; }"""
if "order: 8 !important; }\n    .dashboard-grid .cell-activite        { grid-column: span 3" in texte:
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
    print("OK : dashboard/home.html -- round 19 (3 panneaux retires, 9 panneaux restants reorganises).")