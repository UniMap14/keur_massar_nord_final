CHEMIN = "foncier/templates/foncier/geoportail.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''            <span class="map-legend-swatch" style="background:#c9982e;"></span>
            <span>Parcelle</span>
          </div>
        </div>
      </div>
    </div>'''

nouveau = '''            <span class="map-legend-swatch" style="background:#c9982e;"></span>
            <span>Parcelle</span>
          </div>
          <div class="map-legend-item">
            <span class="map-legend-swatch" style="background:#7b3fa0;"></span>
            <span>Parcelle avec infrastructure</span>
          </div>
        </div>
      </div>
    </div>'''

if "Parcelle avec infrastructure" in contenu:
    print("DEJA FAIT : deja present.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : entree de legende ajoutee.")
else:
    print("ERREUR : bloc exact introuvable.")