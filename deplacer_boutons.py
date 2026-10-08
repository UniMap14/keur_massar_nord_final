# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/fiscalite.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_banner = '''      <p><strong>Documents, taxes et démarches de Keur Massar Nord, réunis en un seul endroit.</strong></p>
      <div class="banner-actions">
        <a href="#" class="btn-primary" id="btnSimulateur">
          <i class="fa-solid fa-calculator"></i> Simuler mon impôt
        </a>
        <a href="{% url 'geoportail' %}" class="btn-outline-w">
          <i class="fa-solid fa-map-location-dot"></i> Voir le géoportail
        </a>
        <a href="{% url 'immatriculation_demande' %}" class="btn-outline-w">
          <i class="fa-solid fa-user-plus"></i> Devenir contribuable
        </a>
        <a href="{% url 'mutation_demande' %}" class="btn-outline-w">
          <i class="fa-solid fa-right-left"></i> Mutation fiscale
        </a>
      </div>
    </div>'''

nouveau_banner = '''      <p><strong>Documents, taxes et démarches de Keur Massar Nord, réunis en un seul endroit.</strong></p>
    </div>'''

if '<div class="banner-actions">' not in contenu:
    resultats.append("Retrait boutons banniere : IGNORE (deja retires)")
elif ancien_banner in contenu:
    contenu = contenu.replace(ancien_banner, nouveau_banner, 1)
    resultats.append("Retrait boutons banniere : OK")
else:
    resultats.append("Retrait boutons banniere : ERREUR introuvable")

ancien_align = '''  .banner-fiscalite .container.fx-hero-inner{
    position: relative;
    z-index: 2;
    display:grid; grid-template-columns:1.15fr .85fr; gap:40px; align-items:start;
  }'''

nouveau_align = '''  .banner-fiscalite .container.fx-hero-inner{
    position: relative;
    z-index: 2;
    display:grid; grid-template-columns:1.15fr .85fr; gap:40px; align-items:center;
  }'''

if "align-items:center;" in contenu and "fx-hero-inner" in contenu:
    resultats.append("Alignement vertical : IGNORE (deja centre)")
elif ancien_align in contenu:
    contenu = contenu.replace(ancien_align, nouveau_align, 1)
    resultats.append("Alignement vertical : OK (centre)")
else:
    resultats.append("Alignement vertical : ERREUR introuvable")

ancien_actions = '''    <a href="{% url 'citoyen_espace' %}" class="tab-btn" style="text-decoration:none;">
      <i class="fa-solid fa-house-user"></i> Mon espace communal
    </a>
    <button class="tab-btn" data-tab="faq" role="tab" id="tab-faq" aria-selected="false" aria-controls="panel-faq">
      <i class="fa-solid fa-circle-question"></i> FAQ
    </button>
  </div>
</div>

<div class="page-body">'''

nouveau_actions = '''    <a href="{% url 'citoyen_espace' %}" class="tab-btn" style="text-decoration:none;">
      <i class="fa-solid fa-house-user"></i> Mon espace communal
    </a>
    <button class="tab-btn" data-tab="faq" role="tab" id="tab-faq" aria-selected="false" aria-controls="panel-faq">
      <i class="fa-solid fa-circle-question"></i> FAQ
    </button>
  </div>
</div>

<div class="container" style="display:flex; gap:12px; flex-wrap:wrap; margin:24px auto 0;">
  <a href="#" class="btn-primary" id="btnSimulateur">
    <i class="fa-solid fa-calculator"></i> Simuler mon impôt
  </a>
  <a href="{% url 'geoportail' %}" class="btn-outline">
    <i class="fa-solid fa-map-location-dot"></i> Voir le géoportail
  </a>
  <a href="{% url 'immatriculation_demande' %}" class="btn-outline">
    <i class="fa-solid fa-user-plus"></i> Devenir contribuable
  </a>
  <a href="{% url 'mutation_demande' %}" class="btn-outline">
    <i class="fa-solid fa-right-left"></i> Mutation fiscale
  </a>
</div>

<div class="page-body">'''

if 'id="btnSimulateur"' in contenu and contenu.count('id="btnSimulateur"') >= 1 and 'margin:24px auto 0;' in contenu:
    resultats.append("Barre d'actions : IGNORE (deja ajoutee)")
elif ancien_actions in contenu:
    contenu = contenu.replace(ancien_actions, nouveau_actions, 1)
    resultats.append("Barre d'actions : OK (boutons replaces sous les onglets)")
else:
    resultats.append("Barre d'actions : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))