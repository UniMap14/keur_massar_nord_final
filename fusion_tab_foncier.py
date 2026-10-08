# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/fiscalite.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_bouton = '''    <button class="tab-btn active" data-tab="general" role="tab" id="tab-general" aria-selected="true" aria-controls="panel-general">
      <i class="fa-solid fa-book-open"></i> Cadre Général
    </button>
    <button class="tab-btn" data-tab="particulier" role="tab" id="tab-particulier" aria-selected="false" aria-controls="panel-particulier">'''

nouveau_bouton = '''    <button class="tab-btn active" data-tab="general" role="tab" id="tab-general" aria-selected="true" aria-controls="panel-general">
      <i class="fa-solid fa-book-open"></i> Cadre Général
    </button>
    <button class="tab-btn" data-tab="foncier" role="tab" id="tab-foncier" aria-selected="false" aria-controls="panel-foncier">
      <i class="fa-solid fa-landmark-dome"></i> Foncier
    </button>
    <button class="tab-btn" data-tab="particulier" role="tab" id="tab-particulier" aria-selected="false" aria-controls="panel-particulier">'''

if 'data-tab="foncier"' in contenu:
    resultats.append("Bouton d'onglet : IGNORE (deja present)")
elif ancien_bouton in contenu:
    contenu = contenu.replace(ancien_bouton, nouveau_bouton, 1)
    resultats.append("Bouton d'onglet : OK (onglet 'Foncier' ajoute)")
else:
    resultats.append("Bouton d'onglet : ERREUR introuvable")

ancien_panel = '''  <div class="tab-panel active" id="panel-general" role="tabpanel" aria-labelledby="tab-general">'''

nouveau_panel = '''  <div class="tab-panel" id="panel-foncier" role="tabpanel" aria-labelledby="tab-foncier">
    <style>
      .fo-doc-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin:28px 0 40px; }
      .fo-doc-card{ background:#fff; border:1px solid #e3d7bc; border-radius:16px; padding:22px 18px; text-align:center; }
      .fo-doc-icon{ width:48px; height:48px; border-radius:50%; margin:0 auto 14px; background:linear-gradient(135deg,#e6bc5c,#d9a52b); display:flex; align-items:center; justify-content:center; font-size:18px; color:#2b1b14; }
      .fo-doc-card h4{ font-size:13.5px; font-weight:700; color:#2b1b14; margin:0 0 7px; }
      .fo-doc-card p{ font-size:12px; line-height:1.55; color:#5a3d2c; margin:0; }
      .fo-legal{ background:#fff; border:1px solid #e3d7bc; border-radius:16px; padding:30px 32px; }
      .fo-legal-item{ display:flex; gap:14px; padding:14px 0; border-bottom:1px solid #f0ebe0; }
      .fo-legal-item:first-child{ padding-top:0; }
      .fo-legal-item:last-child{ border-bottom:none; padding-bottom:0; }
      .fo-legal-item i{ color:#d9a52b; font-size:15px; margin-top:3px; flex-shrink:0; }
      .fo-legal-item h5{ font-size:13px; font-weight:700; color:#2b1b14; margin:0 0 4px; }
      .fo-legal-item p{ font-size:12px; line-height:1.6; color:#5a3d2c; margin:0; }
      @media (max-width: 860px){ .fo-doc-grid{ grid-template-columns:repeat(2,1fr); } }
    </style>

    <h2 class="section-title">Le foncier à Keur Massar Nord</h2>
    <p class="section-sub">Les documents et le cadre légal qui régissent la propriété foncière sur le territoire communal.</p>

    <div class="info-band">
      <i class="fa-solid fa-circle-info"></i>
      <p><strong>Système foncier :</strong> chaque parcelle cadastrée est rattachée à l'un de ces documents, qui atteste du droit d'occupation ou de propriété.</p>
    </div>

    <div class="fo-doc-grid">
      <div class="fo-doc-card">
        <div class="fo-doc-icon"><i class="fa-solid fa-scroll"></i></div>
        <h4>Titre Foncier</h4>
        <p>Le document de propriété le plus sécurisé, immatriculé au Livre Foncier.</p>
      </div>
      <div class="fo-doc-card">
        <div class="fo-doc-icon"><i class="fa-solid fa-file-contract"></i></div>
        <h4>Bail</h4>
        <p>Droit d'occupation temporaire accordé sur le domaine national ou communal.</p>
      </div>
      <div class="fo-doc-card">
        <div class="fo-doc-icon"><i class="fa-solid fa-gavel"></i></div>
        <h4>Délibération Municipale</h4>
        <p>Acte d'affectation décidé par le Conseil municipal pour une parcelle du domaine communal.</p>
      </div>
      <div class="fo-doc-card">
        <div class="fo-doc-icon"><i class="fa-solid fa-stamp"></i></div>
        <h4>Attestation de cession</h4>
        <p>Document attestant le transfert d'un droit d'usage entre particuliers, reconnu par la commune.</p>
      </div>
    </div>

    <h2 class="section-title">Le cadre légal</h2>

    <div class="fo-legal">
      <div class="fo-legal-item">
        <i class="fa-solid fa-building-columns"></i>
        <div>
          <h5>Décret n° 2021-687 du 28 mai 2021</h5>
          <p>Portant création du département de Keur Massar, à l'origine de la réorganisation territoriale de la zone.</p>
        </div>
      </div>
      <div class="fo-legal-item">
        <i class="fa-solid fa-map"></i>
        <div>
          <h5>Décret n° 2021-688 du 28 mai 2021</h5>
          <p>Portant érection des communes de Keur Massar Nord et de Keur Massar Sud, distinctes et autonomes.</p>
        </div>
      </div>
      <div class="fo-legal-item">
        <i class="fa-solid fa-ruler-combined"></i>
        <div>
          <h5>Système de référence spatiale</h5>
          <p>Le cadastre communal est géoréférencé en WGS 84 (EPSG:4326), standard des outils cartographiques modernes.</p>
        </div>
      </div>
    </div>

    <div style="margin-top:32px; display:flex; gap:14px; flex-wrap:wrap;">
      <a href="{% url 'recherche_cadastrale' %}" class="btn-primary">
        <i class="fa-solid fa-magnifying-glass-location"></i> Rechercher une parcelle
      </a>
      <a href="{% url 'geoportail' %}" class="btn-outline">
        <i class="fa-solid fa-map-location-dot"></i> Ouvrir le géoportail
      </a>
    </div>
  </div>

  <div class="tab-panel active" id="panel-general" role="tabpanel" aria-labelledby="tab-general">'''

if 'id="panel-foncier"' in contenu:
    resultats.append("Panneau : IGNORE (deja present)")
elif ancien_panel in contenu:
    contenu = contenu.replace(ancien_panel, nouveau_panel, 1)
    resultats.append("Panneau : OK (contenu Foncier insere)")
else:
    resultats.append("Panneau : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))