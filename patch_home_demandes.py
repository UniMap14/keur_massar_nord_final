# -*- coding: utf-8 -*-
"""
Ajoute 2 tuiles au dashboard-grid : "Dernieres demandes" et "Parcelle
recente", juste apres la tuile "Activite recente". Comme la grille est
en 6 colonnes et comptait 10 tuiles (2 cases vides en ligne 2), ces 2
nouvelles tuiles remplissent exactement l'espace vide existant, sans
ajouter de nouvelle ligne.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

ANCRE = """      Aucune activite recente.
    </div>
    {% endif %}
  </div>
</div>

</div>"""
AJOUT = """      Aucune activite recente.
    </div>
    {% endif %}
  </div>
</div>

<div class="panel cell-demandes">
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

<div class="panel cell-parcelle-recente">
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

</div>"""
if "cell-demandes" in texte:
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
    print("OK : dashboard/home.html -- tuiles 'Dernieres demandes' et 'Parcelle recente' ajoutees.")