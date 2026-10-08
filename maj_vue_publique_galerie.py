CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''def galerie(request):
    """Page publique presentant la galerie photo de la commune."""
    return render(request, 'foncier/galerie.html')'''

nouveau = '''def galerie(request):
    """Page publique presentant la galerie photo de la commune."""
    from .models import PhotoGalerie
    photos = PhotoGalerie.objects.order_by('ordre', '-date_ajout')
    return render(request, 'foncier/galerie.html', {'photos': photos})'''

if "photos = PhotoGalerie.objects" in contenu:
    print("IGNORE : vue galerie deja mise a jour.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : vue galerie mise a jour pour utiliser la base de donnees.")
else:
    print("ERREUR : vue galerie introuvable telle quelle.")