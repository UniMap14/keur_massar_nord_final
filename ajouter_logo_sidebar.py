# -*- coding: utf-8 -*-
"""
Remplace le cercle "K" decoratif de la sidebar par le vrai logo de
Keur Massar Nord (foncier/images/logo.jpeg, deja utilise sur le site
public). Reutilise le CSS existant (.sidebar-brand img, .sidebar-brand
.mark deja stylees de la meme maniere : cercle, bordure doree).

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''    <div class="sidebar-brand">
      <div class="mark">K</div>'''

NOUVEAU = '''    <div class="sidebar-brand">
      <img src="{% static 'foncier/images/logo.jpeg' %}" alt="Logo Keur Massar Nord">'''

if "foncier/images/logo.jpeg" in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (div.mark dans sidebar-brand)")
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