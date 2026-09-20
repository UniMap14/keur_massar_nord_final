CHEMIN = "citoyens/templates/citoyens/espace/modifier_profil.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''    <div class="field">
      <label for="{{ form.telephone.id_for_label }}">Téléphone</label>
      {{ form.telephone }}
      {{ form.telephone.errors }}
    </div>'''

nouveau = '''    <div class="field">
      <label for="{{ form.telephone.id_for_label }}">Téléphone</label>
      {{ form.telephone }}
      {{ form.telephone.errors }}
    </div>

    <div class="field">
      <label for="{{ form.operateur_paiement.id_for_label }}">Opérateur de paiement enregistré</label>
      {{ form.operateur_paiement }}
      <div class="helptext">Pré-rempli automatiquement lors du paiement de vos taxations.</div>
      {{ form.operateur_paiement.errors }}
    </div>'''

if "operateur_paiement" in contenu:
    print("DEJA FAIT : champ deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : champ operateur_paiement ajoute au template.")
else:
    print("ERREUR : ancre introuvable.")