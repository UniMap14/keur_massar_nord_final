CHEMIN = "foncier/templates/dashboard/base.html"

MARQUEUR = "    /* ===== En-tete personnalise agent (topbar) ===== */"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "<style>\n    /* ===== En-tete personnalise agent" in contenu:
    print("DEJA CORRIGE : rien a faire.")
elif MARQUEUR not in contenu:
    print("ERREUR : marqueur introuvable, rien modifie.")
else:
    contenu = contenu.replace(MARQUEUR, "  <style>\n" + MARQUEUR, 1)
    marqueur_fin = "  {% block extra_head %}{% endblock %}"
    idx = contenu.index(marqueur_fin)
    contenu = contenu[:idx] + "  </style>\n\n" + contenu[idx:]
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : CSS correctement enveloppe dans ses propres balises <style>.")