CHEMIN = "foncier/models.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''class Zone(models.Model):
    """Modèle pour représenter les zones/quartiers du shapefile importé."""
    id_shp = models.BigIntegerField(unique=True, verbose_name="ID du shapefile")
    nom = models.CharField(max_length=255, verbose_name="Nom de la zone/quartier")
    layer = models.CharField(max_length=100, verbose_name="Couche du shapefile")
    path = models.CharField(max_length=255, verbose_name="Chemin du fichier source")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie de la zone")
    
    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.layer})"'''

nouveau = '''class Zone(models.Model):
    """Modèle pour représenter les zones/quartiers du shapefile importé."""
    id_shp = models.BigIntegerField(unique=True, verbose_name="ID du shapefile")
    nom = models.CharField(max_length=255, verbose_name="Nom de la zone/quartier")
    layer = models.CharField(max_length=100, verbose_name="Couche du shapefile")
    path = models.CharField(max_length=255, verbose_name="Chemin du fichier source")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie de la zone")
    
    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.layer})"


class QuartierOfficiel(models.Model):
    """Quartiers/villages officiels (zones de recensement)."""
    nom = models.CharField(max_length=255, verbose_name="Nom du quartier")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie du quartier")

    class Meta:
        verbose_name = "Quartier officiel"
        verbose_name_plural = "Quartiers officiels"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class SectionCadastrale(models.Model):
    """Sections cadastrales officielles."""
    numero = models.CharField(max_length=10, verbose_name="Numéro de section")
    geom = models.MultiPolygonField(srid=4326, verbose_name="Géométrie de la section")

    class Meta:
        verbose_name = "Section cadastrale"
        verbose_name_plural = "Sections cadastrales"
        ordering = ['numero']

    def __str__(self):
        return f"Section {self.numero}"'''

if "class QuartierOfficiel" in contenu:
    print("DEJA FAIT : modeles deja presents.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : modeles QuartierOfficiel et SectionCadastrale ajoutes.")
else:
    print("ERREUR : bloc Zone exact introuvable.")