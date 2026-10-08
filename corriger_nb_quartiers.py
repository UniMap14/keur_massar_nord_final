CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "        'nb_quartiers': 104,"
nouveau = "        'nb_quartiers': 86,"

n = contenu.count(ancien)
if n == 0:
    if contenu.count(nouveau):
        print(f"IGNORE : deja corrige ({contenu.count(nouveau)} occurrence(s) a 86).")
    else:
        print("ERREUR : ligne '104' introuvable.")
else:
    contenu = contenu.replace(ancien, nouveau)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print(f"OK : {n} occurrence(s) corrigee(s) de 104 a 86.")