CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''class SectionCadastrale(models.Model):
    """Sections cadastrales officielles."""
    numero = models.CharField(max_length=10, verbose_name="Numéro de section")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie de la section")

    class Meta:
        verbose_name = "Section cadastrale"
        verbose_name_plural = "Sections cadastrales"
        ordering = ['numero']

    def __str__(self):
        return f"Section {self.numero}"'''

nouveau = '''class SectionCadastrale(models.Model):
    """Sections cadastrales officielles."""
    numero = models.CharField(max_length=10, verbose_name="Numéro de section")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie de la section")

    class Meta:
        verbose_name = "Section cadastrale"
        verbose_name_plural = "Sections cadastrales"
        ordering = ['numero']

    def __str__(self):
        return f"Section {self.numero}"


class LimiteAdministrative(models.Model):
    """Limite officielle de la commune (ou autre entite administrative)."""
    nom = models.CharField(max_length=255, verbose_name="Nom de l'entite")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie de la limite")

    class Meta:
        verbose_name = "Limite administrative"
        verbose_name_plural = "Limites administratives"
        ordering = ['nom']

    def __str__(self):
        return self.nom'''

if "class LimiteAdministrative" in contenu:
    print("DEJA FAIT : modele deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : modele LimiteAdministrative ajoute.")
else:
    print("ERREUR : bloc SectionCadastrale exact introuvable.")