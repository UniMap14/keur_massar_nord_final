CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_html = '''    <div class="map-legend">
      <h6>Légende</h6>
      <div class="map-legend-item"><span class="map-legend-swatch" style="background:#6b4a35; border:1px dashed #6b4a35;"></span><span>Zone/Quartier</span></div>
      <div class="map-legend-item"><span class="map-legend-swatch" style="background:#28a745;"></span><span>À jour</span></div>
      <div class="map-legend-item"><span class="map-legend-swatch" style="background:#dc3545;"></span><span>En retard</span></div>
      <div class="map-legend-item"><span class="map-legend-swatch" style="background:#3b82f6;"></span><span>Exonéré</span></div>
    </div>'''

nouveau_html = '''    <div class="map-controls" id="mapControls">
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

if "mapControls" in contenu:
    print("DEJA FAIT : panneau deja present.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    changements += 1
    print("OK : legende remplacee par le panneau de controle.")
else:
    print("ERREUR : bloc HTML introuvable.")

ancien_css = '''  .map-legend-swatch { display: inline-block; width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }'''

nouveau_css = '''  .map-legend-swatch { display: inline-block; width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }

  .map-controls {
    position: absolute; bottom: 14px; left: 14px; z-index: 1100;
    background: rgba(255,255,255,0.97); border: 1px solid rgba(0,0,0,0.08); border-radius: 12px;
    padding: 14px 16px; box-shadow: 0 6px 20px rgba(0,0,0,0.14); font-size: 12.5px; min-width: 210px;
  }
  .mc-header { font-size: 12.5px; font-weight: 700; margin-bottom: 10px; color: #3c2a20; display: flex; align-items: center; gap: 7px; }
  .mc-header i { color: #c9982e; }
  .map-legend-item { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }
  .mc-divider { height: 1px; background: #eee; margin: 10px 0; }
  .mc-label { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: #766c5d; margin-bottom: 8px; }
  .mc-filtre-group { display: flex; flex-direction: column; gap: 4px; }
  .mc-filtre-btn {
    display: flex; align-items: center; gap: 8px; width: 100%; text-align: left;
    background: none; border: 1px solid transparent; border-radius: 8px; padding: 6px 8px;
    font-size: 12.5px; font-family: inherit; cursor: pointer; color: #3c2a20; transition: background .15s ease;
  }
  .mc-filtre-btn:hover { background: #f5efe2; }
  .mc-filtre-btn.active { background: #fdf3e2; border-color: #e8d3a8; font-weight: 700; }
  .mc-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
  .mc-count { margin-left: auto; color: #766c5d; font-weight: 700; font-variant-numeric: tabular-nums; }'''

if ".map-controls {" in contenu:
    print("DEJA FAIT : CSS deja present.")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    changements += 1
    print("OK : CSS du panneau ajoute.")
else:
    print("ERREUR : ancre CSS introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print(f"\n=== {changements} changement(s) enregistres. ===")