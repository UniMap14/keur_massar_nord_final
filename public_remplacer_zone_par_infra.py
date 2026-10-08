CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_html = '''          <label for="filter-zone" style="font-size:13px; font-weight:500; margin-top:8px; display:block;">Zone/Quartier</label>
          <select id="filter-zone" class="search-input">
            <option value="">-- Toutes les zones --</option>
          </select>

          <label for="filter-occupation"'''

nouveau_html = '''          <label style="font-size:13px; font-weight:500; margin-top:8px; display:block;">Infrastructures</label>
          <div id="infraCategorieList" style="display:flex; flex-direction:column; gap:6px; margin-bottom:10px; max-height:180px; overflow-y:auto;">
            <div style="font-size:12px; color:#766c5d;">Chargement...</div>
          </div>

          <label for="filter-occupation"'''

if "infraCategorieList" in contenu:
    print("DEJA FAIT : liste infrastructures deja presente.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    changements += 1
    print("OK : filtre Zone/Quartier retire, liste Infrastructures ajoutee.")
else:
    print("ERREUR : ancre HTML introuvable (etape 1).")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 1/2 : HTML). ===")