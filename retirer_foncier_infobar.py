CHEMIN = "foncier/templates/foncier/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''      <a href="{% url 'foncier_info' %}" class="km-ib-item"><i class="fa-solid fa-landmark-dome"></i> Foncier</a>
'''

n = contenu.count(ancien)
if n == 0:
    print("IGNORE : lien Foncier deja absent de la bande du bas.")
else:
    contenu = contenu.replace(ancien, '')
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print(f"OK : {n} occurrence(s) du lien 'Foncier' retiree(s) de la bande du bas.")