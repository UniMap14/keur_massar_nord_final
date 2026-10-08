CHEMIN = "foncier/templates/dashboard/actualite_list.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '<td>{{ actu.date_publication|date:"d/m/Y H:i" }}</td>'
nouveau = '<td>{{ actu.date_publication|date:"d/m/Y" }}</td>'

if nouveau in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : format de date corrige (suppression de l'heure, absente du champ).")
else:
    print("ERREUR : ligne exacte introuvable.")