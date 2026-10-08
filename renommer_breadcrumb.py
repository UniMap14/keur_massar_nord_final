CHEMIN = "foncier/templates/foncier/fiscalite.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''        <span>Fiscalité</span>'''
nouveau = '''        <span>Foncier &amp; Fiscalité</span>'''

if "Foncier &amp; Fiscalité</span>" in contenu:
    print("IGNORE : fil d'Ariane deja renomme.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : fil d'Ariane renomme en 'Foncier & Fiscalite'.")
else:
    print("ERREUR : fil d'Ariane introuvable tel quel.")