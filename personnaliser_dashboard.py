CHEMIN = "foncier/templates/dashboard/base.html"

ANCRE_AVATAR = '''      <div class="sidebar-user">
        <div class="avatar">{{ request.user.username|slice:":1"|upper }}</div>
        <div class="who">
          {{ request.user.get_full_name|default:request.user.username }}
          <div class="role">{{ libelle_role_utilisateur }}</div>
        </div>
      </div>'''

NOUVEAU_AVATAR = '''      <div class="sidebar-user">
        {% if mon_profil_agent.photo %}
          <img src="{{ mon_profil_agent.photo.url }}" alt="" class="avatar" style="object-fit:cover;">
        {% else %}
          <div class="avatar">{{ request.user.username|slice:":1"|upper }}</div>
        {% endif %}
        <div class="who">
          {{ request.user.get_full_name|default:request.user.username }}
          <div class="role">{{ mon_profil_agent.fonction|default:libelle_role_utilisateur }}</div>
        </div>
      </div>'''

ANCRE_TOPBAR = '''      {% block topbar_extra %}{% endblock %}
    </header>'''

NOUVEAU_TOPBAR = '''      {% block topbar_extra %}{% endblock %}
      <div class="topbar-user-chip">
        {% if mon_profil_agent.photo %}
          <img src="{{ mon_profil_agent.photo.url }}" alt="" class="tuc-avatar" style="object-fit:cover;">
        {% else %}
          <div class="tuc-avatar tuc-avatar-fallback">{{ request.user.username|slice:":1"|upper }}</div>
        {% endif %}
        <div class="tuc-text">
          <div class="tuc-name">{{ request.user.get_full_name|default:request.user.username }}</div>
          <div class="tuc-role">{{ mon_profil_agent.fonction|default:libelle_role_utilisateur }}</div>
        </div>
        <a href="{% url 'dashboard_mon_profil' %}" class="tuc-edit" title="Mon profil"><i class="fa-solid fa-pen"></i></a>
      </div>
    </header>'''

CSS_TOPBAR_CHIP = '''
    /* ===== En-tete personnalise agent (topbar) ===== */
    .topbar-user-chip {
      display: flex; align-items: center; gap: 10px; margin-left: auto;
      padding: 6px 10px 6px 6px; border-radius: 100px;
      background: rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.06);
    }
    .tuc-avatar {
      width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
    }
    .tuc-avatar-fallback {
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(135deg, var(--green-light, #4a9c6d) 0%, var(--green, #2f7a4f) 100%);
      color: #fff; font-weight: 700; font-size: 13px;
    }
    .tuc-text { line-height: 1.25; }
    .tuc-name { font-size: 12.5px; font-weight: 700; }
    .tuc-role { font-size: 10.5px; opacity: 0.6; }
    .tuc-edit {
      color: inherit; opacity: 0.4; margin-left: 4px; font-size: 11px;
      transition: opacity .2s ease;
    }
    .tuc-edit:hover { opacity: 0.9; }
    @media (max-width: 640px) { .tuc-text { display: none; } }

  {% block extra_head %}{% endblock %}'''

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

if ANCRE_AVATAR in contenu and NOUVEAU_AVATAR not in contenu:
    contenu = contenu.replace(ANCRE_AVATAR, NOUVEAU_AVATAR, 1)
    changements += 1
    print("OK : avatar sidebar mis a jour (vraie photo).")
elif NOUVEAU_AVATAR in contenu:
    print("DEJA FAIT : avatar sidebar.")
else:
    print("ERREUR : ancre avatar introuvable.")

if ANCRE_TOPBAR in contenu and "topbar-user-chip" not in contenu:
    contenu = contenu.replace(ANCRE_TOPBAR, NOUVEAU_TOPBAR, 1)
    changements += 1
    print("OK : en-tete personnalise ajoute a la topbar.")
elif "topbar-user-chip" in contenu:
    print("DEJA FAIT : en-tete topbar.")
else:
    print("ERREUR : ancre topbar introuvable.")

if "{% block extra_head %}{% endblock %}\n</head>" in contenu and ".topbar-user-chip {" not in contenu:
    contenu = contenu.replace("  {% block extra_head %}{% endblock %}\n</head>", CSS_TOPBAR_CHIP + "\n</head>", 1)
    changements += 1
    print("OK : CSS du chip topbar ajoute.")
elif ".topbar-user-chip {" in contenu:
    print("DEJA FAIT : CSS du chip.")
else:
    print("ERREUR : ancre CSS introuvable (fin de <head>).")

if changements:
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print(f"\n=== {changements} changement(s) applique(s) et enregistres. ===")
else:
    print("\n=== Aucun changement enregistre. ===")