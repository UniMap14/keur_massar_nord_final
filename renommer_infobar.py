CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''<a href="{% url 'fiscalite' %}" class="km-ib-item"><i class="fa-solid fa-scale-balanced"></i> Fiscalité</a>'''
nouveau = '''<a href="{% url 'fiscalite' %}" class="km-ib-item"><i class="fa-solid fa-scale-balanced"></i> Foncier &amp; Fiscalité</a>'''

n = contenu.count(ancien)
if n == 0:
    if contenu.count(nouveau):
        print(f"IGNORE : deja renomme ({contenu.count(nouveau)} occurrence(s)).")
    else:
        print("ERREUR : lien introuvable.")
else:
    contenu = contenu.replace(ancien, nouveau)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print(f"OK : {n} occurrence(s) renommee(s) en 'Foncier & Fiscalite' dans la bande du bas.")