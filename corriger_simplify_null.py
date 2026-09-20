CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_classe = '''class Simplify(GeomOutputGeoFunc):
    """
    Django n'expose pas ST_Simplify nativement (contrairement à AsGeoJSON) :
    on l'enveloppe soi-même. Génère du SQL : ST_Simplify(geom, tolerance).
    Utilisé pour alléger les géométries envoyées au navigateur sur la carte
    (indispensable à l'échelle de ~40 000 parcelles).
    """
    function = "ST_Simplify"
    arity = 2'''

ajout_classe = ancre_classe + '''


class SimplifyPreserveTopology(GeomOutputGeoFunc):
    """
    Comme Simplify, mais via ST_SimplifyPreserveTopology : garantit une
    géométrie toujours valide (jamais NULL/vide), contrairement à
    ST_Simplify qui peut faire disparaître une toute petite parcelle avec
    une tolérance trop grossière -- ce qui faisait planter json.loads()
    sur la vue d'ensemble complète (40 000 parcelles).
    """
    function = "ST_SimplifyPreserveTopology"
    arity = 2'''

if ancre_classe in contenu and "class SimplifyPreserveTopology" not in contenu:
    contenu = contenu.replace(ancre_classe, ajout_classe, 1)
    changements += 1
    print("OK : classe SimplifyPreserveTopology ajoutee.")
elif "class SimplifyPreserveTopology" in contenu:
    print("DEJA FAIT : classe deja presente.")
else:
    print("ERREUR : ancre de la classe Simplify introuvable.")

ancre_usage = 'Simplify("geom", TOLERANCE_SIMPLIFICATION_TOUTES)'
nouveau_usage = 'SimplifyPreserveTopology("geom", TOLERANCE_SIMPLIFICATION_TOUTES)'

n = contenu.count(ancre_usage)
if n:
    contenu = contenu.replace(ancre_usage, nouveau_usage)
    changements += 1
    print(f"OK : {n} occurrence(s) remplacee(s) dans les vues 'toutes'.")
else:
    print("INFO : aucune occurrence de l'ancien appel trouvee (deja corrige ?).")

if changements:
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print(f"\n=== {changements} changement(s) enregistres. ===")
else:
    print("\n=== Rien enregistre. ===")