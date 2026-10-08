CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''        <li><a href="{% url 'fiscalite' %}">Fiscalité</a></li>
        <li><a href="{% url 'contact' %}">Contact</a></li>'''

nouveau = '''        <li><a href="{% url 'fiscalite' %}">Fiscalité</a></li>
        <li><a href="{% url 'galerie' %}">Galerie</a></li>
        <li><a href="{% url 'actualites' %}">Actualités</a></li>
        <li><a href="{% url 'contact' %}">Contact</a></li>'''

if "url 'galerie'" in contenu:
    print("DEJA FAIT : liens deja presents.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : liens 'Galerie' et 'Actualités' ajoutes au menu.")
else:
    print("ERREUR : bloc exact introuvable.")