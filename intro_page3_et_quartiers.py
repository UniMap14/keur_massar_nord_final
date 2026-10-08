# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# ============================================================
# 1. Texte d'intro "Nos services" sur la Page 3
# ============================================================
ancien = '''<section class="km-bento-section">

  <div class="km-bento-grid-small">'''

nouveau = '''<section class="km-bento-section">

  <div class="km-bento-intro">
    <span class="section-label">Nos services</span>
    <h2>Votre Mairie &agrave; votre service</h2>
    <p>Acc&eacute;dez aux services municipaux essentiels en toute simplicit&eacute;, depuis chez vous ou directement en ligne.</p>
  </div>

  <div class="km-bento-grid-small">'''

if '<span class="section-label">Nos services</span>' in contenu:
    resultats.append("Intro Nos services : IGNORE (deja present)")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    resultats.append("Intro Nos services : OK (ajoutee)")
else:
    resultats.append("Intro Nos services : ERREUR bloc d'ancrage introuvable")

# ============================================================
# 2. Correction 104 -> 86 quartiers
# ============================================================
ancien_q = '{{ nb_quartiers|default:"104" }}'
nouveau_q = '{{ nb_quartiers|default:"86" }}'

if contenu.count(nouveau_q) and not contenu.count(ancien_q):
    resultats.append("Quartiers 86 : IGNORE (deja corrige)")
elif ancien_q in contenu:
    n = contenu.count(ancien_q)
    contenu = contenu.replace(ancien_q, nouveau_q)
    resultats.append(f"Quartiers 86 : OK ({n} occurrence(s) corrigee(s))")
else:
    resultats.append("Quartiers 86 : ERREUR texte '104' introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))