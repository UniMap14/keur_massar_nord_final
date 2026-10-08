CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''<a href="{% url 'fiscalite' %}"><i class="fa-solid fa-scale-balanced"></i> Fiscalité</a>'''
nouveau = '''<a href="{% url 'fiscalite' %}"><i class="fa-solid fa-scale-balanced"></i> Foncier &amp; Fiscalité</a>'''

if "Foncier &amp; Fiscalité</a>" in contenu:
    print("IGNORE : deja renomme dans le menu.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien du menu renomme en 'Foncier & Fiscalite'.")
else:
    print("ERREUR : lien introuvable tel quel.")