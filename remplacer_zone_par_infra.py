CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_html = '''    <div class="panel">
      <div class="panel-header"><h2><i class="fa-solid fa-filter"></i> Filtres</h2></div>
      <div class="panel-body">
        <label style="font-size:12px; font-weight:600; display:block; margin-bottom:4px;">Zone/Quartier</label>
        <select id="filter-zone" class="search-input">
          <option value="">-- Toutes les zones --</option>
        </select>

        {% if peut_fiscal %}'''

nouveau_html = '''    <div class="panel">
      <div class="panel-header"><h2><i class="fa-solid fa-map-pin"></i> Infrastructures</h2></div>
      <div class="panel-body">
        <div id="infraCategorieList" style="display:flex; flex-direction:column; gap:6px; max-height:220px; overflow-y:auto;">
          <div class="ep-empty" style="padding:10px 0;">Chargement...</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header"><h2><i class="fa-solid fa-filter"></i> Filtres</h2></div>
      <div class="panel-body">
        {% if peut_fiscal %}'''

if "infraCategorieList" in contenu:
    print("DEJA FAIT : panneau Infrastructures deja present.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    changements += 1
    print("OK : filtre Zone/Quartier retire, panneau Infrastructures ajoute.")
else:
    print("ERREUR : ancre HTML introuvable (etape 1).")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 1/3 : HTML). ===")