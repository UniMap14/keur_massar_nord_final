CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''<li><a href="{% url 'fiscalite' %}">Fiscalité</a></li>'''
nouveau = '''<li><a href="{% url 'fiscalite' %}">Foncier &amp; Fiscalité</a></li>'''

n = contenu.count(ancien)
if n == 0:
    if contenu.count(nouveau):
        print(f"IGNORE : deja renomme ({contenu.count(nouveau)} occurrence(s)).")
    else:
        print("ERREUR : lien introuvable (verifie manuellement dans le pied de page).")
else:
    contenu = contenu.replace(ancien, nouveau)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print(f"OK : {n} occurrence(s) renommee(s) en 'Foncier & Fiscalite' dans le pied de page.")