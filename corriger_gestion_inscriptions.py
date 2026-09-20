CHEMIN = "citoyens/templates/citoyens/gestion_inscriptions.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''          <td>{{ citoyen.valide_par.get_full_name|default:citoyen.valide_par.username|default:"—" }}</td>'''

nouveau = '''          <td>
            {% if citoyen.valide_par %}
              {{ citoyen.valide_par.get_full_name|default:citoyen.valide_par.username }}
            {% else %}
              —
            {% endif %}
          </td>'''

if nouveau in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : ligne 'valide_par' corrigee, gere maintenant le cas None correctement.")
else:
    print("ERREUR : ligne exacte introuvable.")