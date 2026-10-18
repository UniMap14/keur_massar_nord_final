# -*- coding: utf-8 -*-
"""
Remplace le panneau "Actions rapides" (rangee de boutons plats) par le
bandeau + grille de tuiles. Garde exactement les memes liens/roles
qu'avant (rien de nouveau n'est invente), plus une tuile "Demarches en
ligne" commune a tous les agents (section deja commune, cf.
permissions.py).

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''<!-- ============ ACTIONS RAPIDES ============ -->
<div class="panel">
  <div class="panel-header">
    <h2><i class="fa-solid fa-bolt"></i> Actions rapides</h2>
  </div>
  <div class="panel-body" style="display:flex; gap:12px; flex-wrap:wrap;">
    {% if peut_technique %}<a href="{% url 'dashboard_parcelle_create' %}" class="btn btn-primary btn-sm"><i class="fa-solid fa-plus"></i>Nouvelle parcelle</a>{% endif %}
    {% if peut_fiscal %}
<a href="{% url 'dashboard_parcelle_list' %}?statut_fiscal=EN_RETARD" class="btn btn-outline btn-sm"><i class="fa-solid fa-clock-rotate-left"></i>Voir les retardataires</a>
    <a href="{% url 'dashboard_message_list' %}?statut=non_traite" class="btn btn-outline btn-sm"><i class="fa-solid fa-envelope"></i>Traiter les messages</a>
{% endif %}
  </div>
</div>'''

NOUVEAU = '''<!-- ============ ACTIONS RAPIDES ============ -->
<div class="panel quick-actions-panel">
  <div class="quick-actions-banner">
    <div class="quick-actions-banner-text">
      <div class="eyebrow">Keur Massar Nord</div>
      <div class="title">Que voulez-vous faire ?</div>
    </div>
  </div>
  <div class="quick-actions-grid">
    {% if peut_technique %}
    <a href="{% url 'dashboard_parcelle_create' %}" class="quick-action-tile">
      <div class="quick-action-icon tone-green"><i class="fa-solid fa-plus"></i></div>
      <span>Nouvelle parcelle</span>
    </a>
    {% endif %}
    {% if peut_fiscal %}
    <a href="{% url 'dashboard_parcelle_list' %}?statut_fiscal=EN_RETARD" class="quick-action-tile">
      <div class="quick-action-icon tone-red"><i class="fa-solid fa-clock-rotate-left"></i></div>
      <span>Voir les retardataires</span>
    </a>
    {% endif %}
    <a href="{% url 'dashboard_message_list' %}?statut=non_traite" class="quick-action-tile">
      <div class="quick-action-icon tone-gold"><i class="fa-solid fa-envelope"></i></div>
      <span>Traiter les messages</span>
    </a>
    <a href="{% url 'dashboard_demande_list' %}" class="quick-action-tile">
      <div class="quick-action-icon tone-blue"><i class="fa-solid fa-folder-open"></i></div>
      <span>Démarches en ligne</span>
    </a>
  </div>
</div>'''

if 'class="quick-actions-grid"' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre HTML introuvable (panneau Actions rapides)")
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