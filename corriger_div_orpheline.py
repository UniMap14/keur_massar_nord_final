CHEMIN = "foncier/templates/foncier/geoportail_admin.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''        <button id="btnReinitialiser" class="btn btn-outline btn-sm" style="width:100%;">
          <i class="fa-solid fa-rotate-left"></i> Réinitialiser
        </button>
      </div>
    </div>
    </div>

    <div class="panel">
      <div class="panel-header"><h2><i class="fa-solid fa-download"></i> Exporter</h2></div>'''

nouveau = '''        <button id="btnReinitialiser" class="btn btn-outline btn-sm" style="width:100%;">
          <i class="fa-solid fa-rotate-left"></i> Réinitialiser
        </button>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header"><h2><i class="fa-solid fa-download"></i> Exporter</h2></div>'''

if nouveau in contenu and ancien not in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : balise </div> orpheline supprimee, 'Exporter' rejoint la colonne du geo-sidebar.")
else:
    print("ERREUR : bloc exact introuvable.")