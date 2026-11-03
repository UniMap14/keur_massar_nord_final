# -*- coding: utf-8 -*-
"""
Ajoute le theme "Occupation du sol" a la cartotheque : une regle de
detection dans la vue (foncier/views.py) + une option dans le menu
deroulant du template. Idempotent.
"""

erreurs = []
modifs = 0

# ------------------------------------------------------------------
# 1) Regle de detection dans foncier/views.py
# ------------------------------------------------------------------
CHEMIN_VIEWS = "foncier/views.py"

with open(CHEMIN_VIEWS, "r", encoding="utf-8") as f:
    contenu_views = f.read()

ANCIEN_REGLES = """    regles_theme = [
        ('pente', 'Relief & pentes'),"""

NOUVEAU_REGLES = """    regles_theme = [
        ('occupation du sol', 'Occupation du sol'),
        ('pente', 'Relief & pentes'),"""

if "'occupation du sol'" in contenu_views:
    pass
elif ANCIEN_REGLES not in contenu_views:
    erreurs.append("bloc regles_theme introuvable dans views.py")
else:
    contenu_views = contenu_views.replace(ANCIEN_REGLES, NOUVEAU_REGLES, 1)
    modifs += 1
    with open(CHEMIN_VIEWS, "w", encoding="utf-8") as f:
        f.write(contenu_views)

# ------------------------------------------------------------------
# 2) Option dans le menu deroulant du template
# ------------------------------------------------------------------
CHEMIN_TEMPLATE = "foncier/templates/foncier/cartotheque.html"

with open(CHEMIN_TEMPLATE, "r", encoding="utf-8") as f:
    contenu_template = f.read()

ANCIEN_SELECT = """            <option value="__TOUTES__">Toutes les cartes</option>
            <option value="Relief &amp; pentes">Relief &amp; pentes</option>"""

NOUVEAU_SELECT = """            <option value="__TOUTES__">Toutes les cartes</option>
            <option value="Occupation du sol">Occupation du sol</option>
            <option value="Relief &amp; pentes">Relief &amp; pentes</option>"""

if 'value="Occupation du sol"' in contenu_template:
    pass
elif ANCIEN_SELECT not in contenu_template:
    erreurs.append("bloc select introuvable dans cartotheque.html")
else:
    contenu_template = contenu_template.replace(ANCIEN_SELECT, NOUVEAU_SELECT, 1)
    modifs += 1
    with open(CHEMIN_TEMPLATE, "w", encoding="utf-8") as f:
        f.write(contenu_template)

# ------------------------------------------------------------------
if erreurs:
    print("ERREUR(S) :")
    for e in erreurs:
        print(" -", e)
else:
    print(f"OK : {modifs} fichier(s) modifie(s) (ou deja a jour).")