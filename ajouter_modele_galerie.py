CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''    notes = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Infrastructure"
        verbose_name_plural = "Infrastructures"
        ordering = ['categorie__ordre', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.categorie.label})"'''

nouveau_modele = '''


class PhotoGalerie(models.Model):
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

if "class PhotoGalerie" in contenu:
    print("IGNORE : modele PhotoGalerie deja present.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, ancre + nouveau_modele, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : modele PhotoGalerie ajoute.")
else:
    print("ERREUR : point d'ancrage introuvable.")