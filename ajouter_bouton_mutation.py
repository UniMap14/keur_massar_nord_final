CHEMIN = "foncier/templates/foncier/fiscalite.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''        <a href="{% url 'immatriculation_demande' %}" class="btn-outline-w">
          <i class="fa-solid fa-user-plus"></i> Devenir contribuable
        </a>
      </div>
    </div>'''

nouveau = '''        <a href="{% url 'immatriculation_demande' %}" class="btn-outline-w">
          <i class="fa-solid fa-user-plus"></i> Devenir contribuable
        </a>
        <a href="{% url 'mutation_demande' %}" class="btn-outline-w">
          <i class="fa-solid fa-right-left"></i> Mutation fiscale
        </a>
      </div>
    </div>'''

if "mutation_demande" in contenu and "Mutation fiscale" in contenu:
    print("DEJA FAIT : bouton deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : bouton 'Mutation fiscale' ajoute.")
else:
    print("ERREUR : ancre introuvable.")