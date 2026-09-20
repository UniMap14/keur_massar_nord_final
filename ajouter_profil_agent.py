Q = chr(34)
NL = chr(10)

CHEMIN = "foncier/models.py"

MODELE = (
    NL + NL
    + "class ProfilAgent(models.Model):" + NL
    + "    " + Q*3 + "Informations de profil pour un compte agent/admin (Maire, chef de" + NL
    + "    service...), en complement du compte utilisateur Django standard." + Q*3 + NL
    + "    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name=" + Q + "profil_agent" + Q + ")" + NL
    + "    fonction = models.CharField(" + NL
    + "        max_length=150, blank=True, verbose_name=" + Q + "Fonction" + Q + "," + NL
    + "        help_text=" + Q + "Ex : Maire, Chef du Service Cadastre, Chef du Service Fiscalite" + Q + "," + NL
    + "    )" + NL
    + "    telephone = models.CharField(max_length=20, blank=True, verbose_name=" + Q + "Telephone" + Q + ")" + NL
    + "    photo = models.ImageField(" + NL
    + "        upload_to=" + Q + "profils_agents/" + Q + ", blank=True, null=True," + NL
    + "        verbose_name=" + Q + "Photo de profil" + Q + "," + NL
    + "    )" + NL
    + NL
    + "    class Meta:" + NL
    + "        verbose_name = " + Q + "Profil agent" + Q + NL
    + "        verbose_name_plural = " + Q + "Profils agents" + Q + NL
    + NL
    + "    def __str__(self):" + NL
    + "        return self.fonction or self.user.get_full_name() or self.user.username"
)

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "class ProfilAgent" in contenu:
    print("DEJA PRESENT : rien a faire.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(MODELE)
    print("OK : modele ProfilAgent ajoute a la fin du fichier.")
