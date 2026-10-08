CHEMIN = "foncier/templates/foncier/base.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''        <li><a href="{% url 'foncier_info' %}"><i class="fa-solid fa-landmark-dome"></i> Foncier</a></li>
        <li><a href="{% url 'fiscalite' %}"><i class="fa-solid fa-scale-balanced"></i> Fiscalité</a></li>'''

nouveau = '''        <li><a href="{% url 'fiscalite' %}"><i class="fa-solid fa-scale-balanced"></i> Fiscalité</a></li>'''

if "url 'foncier_info'" not in contenu:
    print("IGNORE : lien Foncier deja retire du menu.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : lien 'Foncier' retire du menu (fusionne dans Fiscalite).")
else:
    print("ERREUR : bloc exact introuvable.")