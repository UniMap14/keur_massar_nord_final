CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''        <li><a href="{% url 'galerie' %}">Galerie</a></li>'''
nouveau = '''        <li><a href="{% url 'galerie' %}">Galerie</a></li>
        <li><a href="{% url 'cartotheque' %}">Cartothèque</a></li>'''

if "url 'cartotheque'" in contenu:
    print("DEJA FAIT : lien deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Cartothèque' ajoute au menu.")
else:
    print("ERREUR : ligne exacte introuvable.")