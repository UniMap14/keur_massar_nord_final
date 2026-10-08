CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_html = '''    <div class="map-controls" id="mapControls">
      <div class="mc-header"><i class="fa-solid fa-sliders"></i> Affichage</div>
      <div class="map-legend-item"><span class="map-legend-swatch" style="background:#6b4a35; border:1px dashed #6b4a35;"></span><span>Zone/Quartier</span></div>
      {% if peut_fiscal %}
      <div class="mc-divider"></div>
      <div class="mc-label">Statut fiscal</div>
      <div class="mc-filtre-group" id="filtreFiscalGroup">
        <button type="button" class="mc-filtre-btn active" data-statut="">
          <span>Toutes</span><span class="mc-count" id="countToutes">—</span>
        </button>
        <button type="button" class="mc-filtre-btn" data-statut="A_JOUR">
          <span class="mc-dot" style="background:#2f7a4f;"></span><span>À jour</span><span class="mc-count" id="countAjour">—</span>
        </button>
        <button type="button" class="mc-filtre-btn" data-statut="EN_RETARD">
          <span class="mc-dot" style="background:#b23b2e;"></span><span>En retard</span><span class="mc-count" id="countRetard">—</span>
        </button>
        <button type="button" class="mc-filtre-btn" data-statut="EXONERE">
          <span class="mc-dot" style="background:#3468a8;"></span><span>Exonéré</span><span class="mc-count" id="countExonere">—</span>
        </button>
      </div>
      {% endif %}
    </div>'''

nouveau_html = '''    <div class="map-controls" id="mapControls">
      <div class="mc-header"><i class="fa-solid fa-layer-group"></i> Légende</div>
      <div class="map-legend-item"><span class="map-legend-swatch" style="background:#6b4a35; border:1px dashed #6b4a35;"></span><span>Zone/Quartier</span></div>
    </div>'''

if nouveau_html in contenu:
    print("DEJA FAIT : panneau flottant deja simplifie.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    changements += 1
    print("OK : panneau flottant simplifie (fiscal retire, integre au panneau Filtres a la place).")
else:
    print("ERREUR : bloc HTML introuvable (etape 1).")

ancien_select = '''        <label style="font-size:12px; font-weight:600; display:block; margin-bottom:4px;">Statut fiscal</label>
        <select id="filter-statut" class="search-input" style="margin-bottom:8px;">
          <option value="">-- Tous les statuts --</option>
          <option value="A_JOUR">À jour</option>
          <option value="EN_RETARD">En retard</option>
          <option value="EXONERE">Exonéré</option>
        </select>'''

nouveau_select = '''        {% if peut_fiscal %}
        <label style="font-size:12px; font-weight:600; display:block; margin-bottom:4px;">Statut fiscal</label>
        <select id="filter-statut" class="search-input" style="margin-bottom:8px;">
          <option value="">-- Tous les statuts (neutre) --</option>
          <option value="TOUS_COLORES">Toutes (avec couleurs)</option>
          <option value="A_JOUR">À jour uniquement</option>
          <option value="EN_RETARD">En retard uniquement</option>
          <option value="EXONERE">Exonéré uniquement</option>
        </select>
        {% endif %}'''

if "TOUS_COLORES" in contenu.split("function applyFilters")[0]:
    print("DEJA FAIT : select deja modifie.")
elif ancien_select in contenu:
    contenu = contenu.replace(ancien_select, nouveau_select, 1)
    changements += 1
    print("OK : select 'Statut fiscal' reserve a l'agent fiscal, option couleurs ajoutee.")
else:
    print("ERREUR : ancre select introuvable (etape 2).")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres (partie 1/2). ===")