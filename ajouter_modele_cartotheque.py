CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''class PhotoGalerie(models.Model):
    """Une photo affichee dans la galerie publique du site (page 'La commune
    en images'). Geree depuis le tableau de bord, sans toucher au code."""

    titre = models.CharField(max_length=200, verbose_name="Titre / légende")
    photo = models.ImageField(upload_to='galerie/', verbose_name="Photo")
    ordre = models.PositiveIntegerField(
        default=0,
        help_text="Détermine l'ordre d'affichage (les plus petits nombres en premier).",
    )
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo de la galerie"
        verbose_name_plural = "Photos de la galerie"
        ordering = ['ordre', '-date_ajout']

    def __str__(self):
        return self.titre'''

nouveau_modele = '''


class CarteThematique(models.Model):
    """Une carte d'analyse (MNT, pente, densite...) affichee sur la page
    publique 'Cartotheque'. Geree depuis le tableau de bord."""

    titre = models.CharField(max_length=200, verbose_name="Titre de la carte")
    explication = models.TextField(
        verbose_name="Explication / signification",
        help_text="Quelques phrases expliquant ce que montre cette carte et pourquoi elle est utile.",
    )
    image = models.ImageField(upload_to='cartotheque/', verbose_name="Image de la carte")
    ordre = models.PositiveIntegerField(
        default=0,
        help_text="Détermine l'ordre d'affichage (les plus petits nombres en premier).",
    )
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Carte thématique"
        verbose_name_plural = "Cartothèque (cartes thématiques)"
        ordering = ['ordre', '-date_ajout']

    def __str__(self):
        return self.titre'''

if "class CarteThematique" in contenu:
    print("IGNORE : modele CarteThematique deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, ancre + nouveau_modele, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : modele CarteThematique ajoute.")
else:
    print("ERREUR : point d'ancrage introuvable (le modele PhotoGalerie n'est peut-etre pas exactement comme prevu).")