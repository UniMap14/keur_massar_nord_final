CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- 1. CSS du sous-menu repliable ---
MARQUEUR_CSS = ".sidebar-subgroup summary"

ancien_css = '''    /* ===== micro-interaction générale sur les liens de la sidebar "autre" ===== */'''

nouveau_css = '''    /* ===== SOUS-MENU REPLIABLE (regroupe les procedures fiscales) ===== */
    .sidebar-subgroup { margin-bottom: 2px; }
    .sidebar-subgroup summary {
      list-style: none;
      cursor: pointer;
      display: flex; align-items: center; gap: 12px;
      padding: 10px 12px;
      border-radius: 8px;
      color: rgba(255,255,255,0.78);
      font-size: 13.5px;
      transition: background .15s ease, color .15s ease;
    }
    .sidebar-subgroup summary::-webkit-details-marker { display: none; }
    .sidebar-subgroup summary::marker { content: ""; }
    .sidebar-subgroup summary:hover { background: rgba(255,255,255,0.07); color: #fff; }
    .sidebar-subgroup summary i.nav-icon { width: 18px; text-align: center; font-size: 14px; opacity: 0.7; flex-shrink: 0; }
    .sidebar-subgroup summary .chevron { margin-left: auto; font-size: 10px; transition: transform .2s ease; opacity: 0.55; }
    .sidebar-subgroup[open] summary .chevron { transform: rotate(90deg); }
    .sidebar-subgroup[open] summary { color: #fff; }
    .sidebar-subgroup .sidebar-nav { padding-left: 16px; margin-top: 2px; }

    /* ===== micro-interaction générale sur les liens de la sidebar "autre" ===== */'''

if MARQUEUR_CSS in contenu:
    resultats.append("IGNORE : CSS du sous-menu deja present.")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("OK : CSS du sous-menu repliable ajoute.")
else:
    resultats.append("ERREUR : bloc CSS ancre introuvable.")

# --- 2. Restructuration du bloc Fiscalite : 4 liens courants + sous-menu de 7 ---
MARQUEUR_HTML = 'class="sidebar-subgroup"'

ancien_html = '''    {% if peut_fiscal %}
    <div class="sidebar-section-label">Fiscalité</div>
    <ul class="sidebar-nav">
      <li><a href="{% url 'dashboard_declaration_list' %}" class="sidebar-link {% if active_section == 'declarations' %}active{% endif %}">
        <i class="fa-solid fa-file-signature nav-icon"></i> Déclarations fiscales
      </a></li>
      <li><a href="{% url 'dashboard_recours_list' %}" class="sidebar-link {% if active_section == 'recours' %}active{% endif %}">
        <i class="fa-solid fa-scale-balanced nav-icon"></i> Recours fiscaux
      </a></li>
      <li><a href="{% url 'dashboard_immatriculation_list' %}" class="sidebar-link {% if active_section == 'immatriculations' %}active{% endif %}">
        <i class="fa-solid fa-user-plus nav-icon"></i> Premières immatriculations
      </a></li>
      <li><a href="{% url 'dashboard_exoneration_list' %}" class="sidebar-link {% if active_section == 'exonerations' %}active{% endif %}">
        <i class="fa-solid fa-house-circle-check nav-icon"></i> Exonérations fiscales
      </a></li>
      <li><a href="{% url 'dashboard_plan_paiement_list' %}" class="sidebar-link {% if active_section == 'plans_paiement' %}active{% endif %}">
        <i class="fa-solid fa-calendar-days nav-icon"></i> Plans de paiement
      </a></li>
      <li><a href="{% url 'dashboard_mutation_list' %}" class="sidebar-link {% if active_section == 'mutations' %}active{% endif %}">
        <i class="fa-solid fa-right-left nav-icon"></i> Mutations fiscales
      </a></li>
      <li><a href="{% url 'dashboard_morcellement_fusion_list' %}" class="sidebar-link {% if active_section == 'morcellement_fusion' %}active{% endif %}">
        <i class="fa-solid fa-object-ungroup nav-icon"></i> Morcellement / Fusion
      </a></li>
      <li><a href="{% url 'dashboard_contribuable_list' %}" class="sidebar-link {% if active_section == 'contribuables' %}active{% endif %}">
        <i class="fa-solid fa-id-card nav-icon"></i> Contribuables
      </a></li>
      <li><a href="{% url 'dashboard_taxation_list' %}" class="sidebar-link {% if active_section == 'taxations' %}active{% endif %}">
        <i class="fa-solid fa-file-invoice-dollar nav-icon"></i> Taxations
      </a></li>
      <li><a href="{% url 'dashboard_paiement_list' %}" class="sidebar-link {% if active_section == 'paiements' %}active{% endif %}">
        <i class="fa-solid fa-credit-card nav-icon"></i> Paiements
      </a></li>
      <li><a href="{% url 'dashboard_typetaxe_list' %}" class="sidebar-link {% if active_section == 'types_taxe' %}active{% endif %}">
        <i class="fa-solid fa-tags nav-icon"></i> Types de taxe
      </a></li>
    </ul>
    {% endif %}'''

nouveau_html = '''    {% if peut_fiscal %}
    <div class="sidebar-section-label">Fiscalité</div>
    <ul class="sidebar-nav">
      <li><a href="{% url 'dashboard_contribuable_list' %}" class="sidebar-link {% if active_section == 'contribuables' %}active{% endif %}">
        <i class="fa-solid fa-id-card nav-icon"></i> Contribuables
      </a></li>
      <li><a href="{% url 'dashboard_taxation_list' %}" class="sidebar-link {% if active_section == 'taxations' %}active{% endif %}">
        <i class="fa-solid fa-file-invoice-dollar nav-icon"></i> Taxations
      </a></li>
      <li><a href="{% url 'dashboard_paiement_list' %}" class="sidebar-link {% if active_section == 'paiements' %}active{% endif %}">
        <i class="fa-solid fa-credit-card nav-icon"></i> Paiements
      </a></li>
      <li><a href="{% url 'dashboard_typetaxe_list' %}" class="sidebar-link {% if active_section == 'types_taxe' %}active{% endif %}">
        <i class="fa-solid fa-tags nav-icon"></i> Types de taxe
      </a></li>
      <li>
        <details class="sidebar-subgroup" {% if active_section == 'declarations' or active_section == 'recours' or active_section == 'immatriculations' or active_section == 'exonerations' or active_section == 'plans_paiement' or active_section == 'mutations' or active_section == 'morcellement_fusion' %}open{% endif %}>
          <summary>
            <i class="fa-solid fa-folder-tree nav-icon"></i> Procédures &amp; validations
            <i class="fa-solid fa-chevron-right chevron"></i>
          </summary>
          <ul class="sidebar-nav">
            <li><a href="{% url 'dashboard_declaration_list' %}" class="sidebar-link {% if active_section == 'declarations' %}active{% endif %}">
              <i class="fa-solid fa-file-signature nav-icon"></i> Déclarations fiscales
            </a></li>
            <li><a href="{% url 'dashboard_recours_list' %}" class="sidebar-link {% if active_section == 'recours' %}active{% endif %}">
              <i class="fa-solid fa-scale-balanced nav-icon"></i> Recours fiscaux
            </a></li>
            <li><a href="{% url 'dashboard_immatriculation_list' %}" class="sidebar-link {% if active_section == 'immatriculations' %}active{% endif %}">
              <i class="fa-solid fa-user-plus nav-icon"></i> Premières immatriculations
            </a></li>
            <li><a href="{% url 'dashboard_exoneration_list' %}" class="sidebar-link {% if active_section == 'exonerations' %}active{% endif %}">
              <i class="fa-solid fa-house-circle-check nav-icon"></i> Exonérations fiscales
            </a></li>
            <li><a href="{% url 'dashboard_plan_paiement_list' %}" class="sidebar-link {% if active_section == 'plans_paiement' %}active{% endif %}">
              <i class="fa-solid fa-calendar-days nav-icon"></i> Plans de paiement
            </a></li>
            <li><a href="{% url 'dashboard_mutation_list' %}" class="sidebar-link {% if active_section == 'mutations' %}active{% endif %}">
              <i class="fa-solid fa-right-left nav-icon"></i> Mutations fiscales
            </a></li>
            <li><a href="{% url 'dashboard_morcellement_fusion_list' %}" class="sidebar-link {% if active_section == 'morcellement_fusion' %}active{% endif %}">
              <i class="fa-solid fa-object-ungroup nav-icon"></i> Morcellement / Fusion
            </a></li>
          </ul>
        </details>
      </li>
    </ul>
    {% endif %}'''

if MARQUEUR_HTML in contenu:
    resultats.append("IGNORE : sous-menu Fiscalite deja regroupe.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("OK : sous-menu 'Procedures & validations' cree (7 liens regroupes).")
else:
    resultats.append("ERREUR : bloc HTML Fiscalite exact introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))