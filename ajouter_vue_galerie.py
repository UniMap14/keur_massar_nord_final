CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = "def signalement(request):"

nouveau = '''def galerie(request):
    """Page publique presentant la galerie photo de la commune."""
    return render(request, 'foncier/galerie.html')


def signalement(request):'''

if "def galerie(request):" in contenu:
    print("DEJA FAIT : vue 'galerie' deja presente.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : vue 'galerie' ajoutee.")
else:
    print("ERREUR : marqueur introuvable.")