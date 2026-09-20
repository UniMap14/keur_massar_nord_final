Q = chr(34)
NL = chr(10)

CHEMIN = "foncier/models.py"
ANCRE = (
    "    dernier_rappel_envoye = models.DateField(" + NL
    + "        blank=True, null=True," + NL
    + "        verbose_name=" + Q + "Dernier rappel d'échéance envoyé" + Q + "," + NL
    + "        help_text=" + Q + "Rempli automatiquement par la commande envoyer_rappels_echeances, pour ne jamais envoyer deux fois le même rappel." + Q + "," + NL
    + "    )"
)

AJOUT = (
    NL
    + "    simulation_fiscale = models.BooleanField(" + NL
    + "        default=False, verbose_name=" + Q + "Taxation simulée" + Q + "," + NL
    + "        help_text=(" + NL
    + "            " + Q + "Coché si cette taxation provient d'une simulation académique, " + Q + NL
    + "            " + Q + "et non d'une émission réelle par les services de la commune." + Q + NL
    + "        )," + NL
    + "    )"
)

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

if "simulation_fiscale = models.BooleanField" in contenu and "class Taxation" in contenu.split("simulation_fiscale = models.BooleanField")[0][-2000:]:
    print("ATTENTION : un champ simulation_fiscale existe deja quelque part avant Taxation, verification manuelle recommandee.")

if ANCRE not in contenu:
    print("ERREUR : ancre introuvable, rien modifie.")
else:
    # Verifie qu'on ne modifie que l'occurrence dans la classe Taxation
    idx = contenu.index(ANCRE)
    contenu = contenu[:idx] + ANCRE + AJOUT + contenu[idx+len(ANCRE):]
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champ simulation_fiscale ajoute a Taxation.")
