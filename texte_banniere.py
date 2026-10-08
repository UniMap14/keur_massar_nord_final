# -*- coding: utf-8 -*-
CHEMIN = "foncier/templates/foncier/fiscalite.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

ancien = '''      <div class="banner-badge"><span class="badge-dot"></span>Suivi fiscal intégré</div>
      <h1>Comprenez et pilotez la fiscalité foncière avec transparence.</h1>
      <p><strong>Un espace clair pour suivre le système fiscal, les obligations des contribuables, les procédures et la performance du recouvrement à Keur Massar Nord.</strong></p>'''

nouveau = '''      <div class="banner-badge"><span class="badge-dot"></span>Foncier &amp; Fiscalité</div>
      <h1>Votre foncier, votre fiscalité, en toute clarté.</h1>
      <p><strong>Documents, taxes et démarches de Keur Massar Nord, réunis en un seul endroit.</strong></p>'''

if "Votre foncier, votre fiscalité" in contenu:
    resultats.append("Texte banniere : IGNORE (deja raccourci)")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    resultats.append("Texte banniere : OK (reecrit et raccourci)")
else:
    resultats.append("Texte banniere : ERREUR introuvable")

ancien_titre_valeurs = '''<h3>Les valeurs de notre fiscalité</h3>'''
nouveau_titre_valeurs = '''<h3>Nos valeurs</h3>'''

if "<h3>Nos valeurs</h3>" in contenu:
    resultats.append("Titre valeurs : IGNORE (deja raccourci)")
elif ancien_titre_valeurs in contenu:
    contenu = contenu.replace(ancien_titre_valeurs, nouveau_titre_valeurs, 1)
    resultats.append("Titre valeurs : OK (raccourci)")
else:
    resultats.append("Titre valeurs : ERREUR introuvable")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))