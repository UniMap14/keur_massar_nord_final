# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/fiscalite.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien_html = '''      <div class="fx-values-grid">
        <div class="fx-value-item">
          <i class="fa-solid fa-landmark"></i>
          <strong>Équité</strong>
          <span>Garantir une fiscalité juste pour tous.</span>
        </div>
        <div class="fx-value-item">
          <i class="fa-solid fa-file-shield"></i>
          <strong>Transparence</strong>
          <span>Assurer une gestion claire et fiable.</span>
        </div>
        <div class="fx-value-item">
          <i class="fa-solid fa-sack-dollar"></i>
          <strong>Performance</strong>
          <span>Optimiser le recouvrement des recettes fiscales.</span>
        </div>
        <div class="fx-value-item">
          <i class="fa-solid fa-chart-line"></i>
          <strong>Développement</strong>
          <span>Financer les projets et services publics locaux.</span>
        </div>
      </div>'''

nouveau_html = '''      <div class="fx-values-grid">
        <div class="fx-value-item">
          <i class="fa-solid fa-landmark"></i>
          <strong>Équité</strong>
          <span>Garantir une gestion juste pour tous.</span>
        </div>
        <div class="fx-value-item">
          <i class="fa-solid fa-file-shield"></i>
          <strong>Transparence</strong>
          <span>Assurer une gestion claire et fiable.</span>
        </div>
      </div>'''

if "Performance" not in contenu and "Développement</strong>" not in contenu:
    resultats.append("Nombre de valeurs : IGNORE (deja reduit)")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("Nombre de valeurs : OK (4 -> 2)")
else:
    resultats.append("Nombre de valeurs : ERREUR introuvable")

ancien_css = '''  .fx-values-panel{ background:#fff; color:#2a2420; border-radius:16px; box-shadow:0 16px 40px rgba(63,42,28,.18); padding:26px; }
  .fx-values-panel h3{ font-family:'Playfair Display', serif; font-size:18.5px; font-weight:700; margin:0 0 18px; position:relative; padding-bottom:10px; }
  .fx-values-panel h3::after{ content:""; position:absolute; left:0; bottom:0; width:44px; height:3px; background:#c9982e; border-radius:2px; }
  .fx-values-grid{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
  .fx-value-item{ background:#f1e9d8; border-radius:10px; padding:18px 12px; text-align:center; }
  .fx-value-item i{ color:#c9982e; font-size:19px; margin-bottom:9px; display:block; }
  .fx-value-item strong{ font-family:'Playfair Display', serif; font-size:14.5px; display:block; color:#3f2a1c; margin-bottom:5px; }
  .fx-value-item span{ font-size:11.5px; color:#6f655a; line-height:1.5; display:block; }'''

nouveau_css = '''  .fx-values-panel{ background:#fff; color:#2a2420; border-radius:14px; box-shadow:0 16px 40px rgba(63,42,28,.18); padding:18px; max-width:340px; }
  .fx-values-panel h3{ font-family:'Playfair Display', serif; font-size:15.5px; font-weight:700; margin:0 0 12px; position:relative; padding-bottom:8px; }
  .fx-values-panel h3::after{ content:""; position:absolute; left:0; bottom:0; width:34px; height:3px; background:#c9982e; border-radius:2px; }
  .fx-values-grid{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }
  .fx-value-item{ background:#f1e9d8; border-radius:9px; padding:13px 10px; text-align:center; }
  .fx-value-item i{ color:#c9982e; font-size:15px; margin-bottom:6px; display:block; }
  .fx-value-item strong{ font-family:'Playfair Display', serif; font-size:12.5px; display:block; color:#3f2a1c; margin-bottom:3px; }
  .fx-value-item span{ font-size:10px; color:#6f655a; line-height:1.4; display:block; }'''

if "max-width:340px;" in contenu:
    resultats.append("Taille compacte : IGNORE (deja applique)")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("Taille compacte : OK (panneau reduit)")
else:
    resultats.append("Taille compacte : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))