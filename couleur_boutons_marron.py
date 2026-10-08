# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/fiscalite.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''<div class="container" style="display:flex; gap:12px; flex-wrap:wrap; margin:24px auto 0;">
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
</div>'''

nouveau = '''<div class="container" style="display:flex; gap:12px; flex-wrap:wrap; margin:24px auto 0;">
  <a href="#" id="btnSimulateur" style="display:inline-flex; align-items:center; gap:9px; background:#6b4a35; color:#fff; font-weight:700; font-size:13.5px; padding:12px 22px; border-radius:999px; text-decoration:none;">
    <i class="fa-solid fa-calculator"></i> Simuler mon impôt
  </a>
  <a href="{% url 'geoportail' %}" style="display:inline-flex; align-items:center; gap:9px; background:#fff; color:#6b4a35; font-weight:700; font-size:13.5px; padding:11px 21px; border-radius:999px; border:1.5px solid #6b4a35; text-decoration:none;">
    <i class="fa-solid fa-map-location-dot"></i> Voir le géoportail
  </a>
  <a href="{% url 'immatriculation_demande' %}" style="display:inline-flex; align-items:center; gap:9px; background:#fff; color:#6b4a35; font-weight:700; font-size:13.5px; padding:11px 21px; border-radius:999px; border:1.5px solid #6b4a35; text-decoration:none;">
    <i class="fa-solid fa-user-plus"></i> Devenir contribuable
  </a>
  <a href="{% url 'mutation_demande' %}" style="display:inline-flex; align-items:center; gap:9px; background:#fff; color:#6b4a35; font-weight:700; font-size:13.5px; padding:11px 21px; border-radius:999px; border:1.5px solid #6b4a35; text-decoration:none;">
    <i class="fa-solid fa-right-left"></i> Mutation fiscale
  </a>
</div>'''

if 'background:#6b4a35; color:#fff;' in contenu and 'id="btnSimulateur"' in contenu:
    print("IGNORE : boutons deja colores en marron.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : les 4 boutons sont maintenant colores en marron, clairement visibles.")
else:
    print("ERREUR : bloc introuvable tel quel.")