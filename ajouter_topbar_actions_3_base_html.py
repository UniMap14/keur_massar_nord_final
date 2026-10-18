# -*- coding: utf-8 -*-
"""
Ajoute au topbar de dashboard/base.html : une barre de recherche rapide
de parcelles (visible seulement pour le service technique), une cloche
de notifications avec badge + panneau deroulant, et un bouton plein
ecran. Ajoute aussi le JS d'interaction correspondant.

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# 1) HTML : barre de recherche + bloc d'actions, avant le chip utilisateur
ANCIEN_HTML = '''      {% block topbar_extra %}{% endblock %}
      <div class="topbar-user-chip">'''

NOUVEAU_HTML = '''      {% block topbar_extra %}{% endblock %}

      {% if peut_technique %}
      <form method="get" action="{% url 'dashboard_parcelle_list' %}" class="topbar-search">
        <input type="text" name="q" placeholder="Rechercher une parcelle, un proprietaire...">
      </form>
      {% endif %}

      <div class="topbar-actions">
        <button type="button" class="topbar-icon-btn" id="topbarNotifBtn" aria-label="Notifications">
          <i class="fa-regular fa-bell"></i>
          {% if nb_notifications_total %}<span class="topbar-notif-badge">{{ nb_notifications_total }}</span>{% endif %}
        </button>
        <div class="topbar-notif-panel" id="topbarNotifPanel">
          <div class="topbar-notif-panel-header">Notifications</div>
          {% if nb_messages_non_traites %}
          <a href="{% url 'dashboard_message_list' %}" class="topbar-notif-item">
            <span>Messages non traites</span><span class="count">{{ nb_messages_non_traites }}</span>
          </a>
          {% endif %}
          {% if nb_demandes_a_traiter %}
          <a href="{% url 'dashboard_demande_list' %}" class="topbar-notif-item">
            <span>Demarches a traiter</span><span class="count">{{ nb_demandes_a_traiter }}</span>
          </a>
          {% endif %}
          {% if nb_inscriptions_en_attente %}
          <a href="{% url 'gestion_inscriptions' %}" class="topbar-notif-item">
            <span>Inscriptions en attente</span><span class="count">{{ nb_inscriptions_en_attente }}</span>
          </a>
          {% endif %}
          {% if peut_technique and nb_signalements_en_cours %}
          <a href="{% url 'dashboard_signalement_list' %}" class="topbar-notif-item">
            <span>Signalements en cours</span><span class="count">{{ nb_signalements_en_cours }}</span>
          </a>
          {% endif %}
          {% if not nb_notifications_total %}
          <div class="topbar-notif-empty">Rien a signaler pour le moment.</div>
          {% endif %}
        </div>
        <button type="button" class="topbar-icon-btn" id="topbarFullscreenBtn" aria-label="Plein ecran">
          <i class="fa-solid fa-expand"></i>
        </button>
      </div>

      <div class="topbar-user-chip">'''

if 'id="topbarNotifBtn"' in contenu:
    pass
elif ANCIEN_HTML not in contenu:
    erreurs.append("ancre HTML introuvable (topbar_extra / topbar-user-chip)")
else:
    contenu = contenu.replace(ANCIEN_HTML, NOUVEAU_HTML, 1)
    remplacements_ok += 1

# 2) JS : interactions (ouverture panneau, plein ecran)
ANCIEN_JS = '''    });
  })();
</script>

{% block extra_js %}{% endblock %}'''

NOUVEAU_JS = '''    });
  })();

  // Notifications : ouverture/fermeture du panneau au clic sur la cloche
  (function () {
    var btn = document.getElementById("topbarNotifBtn");
    var panel = document.getElementById("topbarNotifPanel");
    if (!btn || !panel) return;

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      panel.classList.toggle("open");
    });
    document.addEventListener("click", function (e) {
      if (panel.classList.contains("open") && !panel.contains(e.target) && e.target !== btn) {
        panel.classList.remove("open");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") panel.classList.remove("open");
    });
  })();

  // Plein ecran : bascule sur le document entier
  (function () {
    var btn = document.getElementById("topbarFullscreenBtn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(function () {});
      } else {
        document.exitFullscreen();
      }
    });
  })();
</script>

{% block extra_js %}{% endblock %}'''

if 'topbarFullscreenBtn' in contenu and 'requestFullscreen' in contenu:
    pass
elif ANCIEN_JS not in contenu:
    erreurs.append("ancre JS introuvable (fin du script flash + extra_js)")
else:
    contenu = contenu.replace(ANCIEN_JS, NOUVEAU_JS, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")