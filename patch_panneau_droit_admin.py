# -*- coding: utf-8 -*-
"""
Ajoute un bouton discret permettant de masquer/afficher le panneau droit
du geoportail admin, avec agrandissement fluide de la carte Leaflet et
recalcul automatique de ses dimensions (invalidateSize).
Idempotent : si le patch est deja applique, le script le signale et ne
touche a rien.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/foncier/geoportail_admin.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) CSS : grille repliable + bouton + sidebar qui s'estompe
# ---------------------------------------------------------------------
ANCRE_CSS = """  .geo-wrap {
    display: grid;
    grid-template-columns: 280px minmax(0, 1fr) 280px;
    gap: 16px;
    height: 100%;
  }

  .geo-sidebar-left, .geo-sidebar-right {
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }"""
AJOUT_CSS = """

  .geo-wrap { transition: grid-template-columns .3s ease; }
  .geo-wrap.panneau-droit-masque { grid-template-columns: 280px minmax(0, 1fr) 0px; }
  .geo-sidebar-right { transition: opacity .2s ease; }
  .geo-wrap.panneau-droit-masque .geo-sidebar-right { opacity: 0; pointer-events: none; overflow: hidden; }

  .geo-panel-toggle-btn {
    position: absolute;
    top: 50%;
    right: 14px;
    transform: translateY(-50%);
    width: 30px;
    height: 46px;
    border-radius: 10px;
    border: 1px solid var(--geo-bordure);
    background: rgba(255,255,255,0.97);
    color: var(--geo-brun-fonce);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px rgba(0,0,0,0.14);
    font-size: 13px;
    z-index: 1150;
    transition: background .15s ease;
  }
  .geo-panel-toggle-btn:hover { background: #faf6ec; }"""
if "panneau-droit-masque" in texte:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, ANCRE_CSS + AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# 2) HTML : bouton place dans la colonne carte, pres du bord droit
# ---------------------------------------------------------------------
ANCRE_HTML = """        <button type="button" class="geo-fullscreen-btn" id="btnFullscreen" title="Plein écran">
          <i class="fa-solid fa-expand"></i>
        </button>
      </div>"""
AJOUT_HTML = """        <button type="button" class="geo-fullscreen-btn" id="btnFullscreen" title="Plein écran">
          <i class="fa-solid fa-expand"></i>
        </button>
      </div>

      <button type="button" class="geo-panel-toggle-btn" id="btnTogglePanneauDroit" title="Masquer le panneau">
        <i class="fa-solid fa-angles-right"></i>
      </button>"""
if "btnTogglePanneauDroit" in texte:
    pass
elif ANCRE_HTML not in texte:
    erreurs.append("ANCRE_HTML introuvable")
else:
    texte = texte.replace(ANCRE_HTML, AJOUT_HTML, 1)

# ---------------------------------------------------------------------
# 3) JS : fonction de bascule (placee juste avant basculerPleinEcran)
# ---------------------------------------------------------------------
ANCRE_JS = """  function basculerPleinEcran() {
    const frame = document.getElementById('mapFrame');"""
AJOUT_JS = """  function basculerPanneauDroit() {
    const conteneur = document.querySelector('.geo-wrap');
    const bouton = document.getElementById('btnTogglePanneauDroit');
    if (!conteneur) return;
    const masque = conteneur.classList.toggle('panneau-droit-masque');
    if (bouton) {
      const icone = bouton.querySelector('i');
      if (icone) icone.className = masque ? 'fa-solid fa-angles-left' : 'fa-solid fa-angles-right';
      bouton.title = masque ? 'Afficher le panneau' : 'Masquer le panneau';
    }
    setTimeout(function () { if (map) map.invalidateSize(); }, 320);
  }

  function basculerPleinEcran() {
    const frame = document.getElementById('mapFrame');"""
if "function basculerPanneauDroit" in texte:
    pass
elif ANCRE_JS not in texte:
    erreurs.append("ANCRE_JS introuvable")
else:
    texte = texte.replace(ANCRE_JS, AJOUT_JS, 1)

# ---------------------------------------------------------------------
# 4) JS : branchement de l'evenement
# ---------------------------------------------------------------------
ANCRE_EVT = "    onEvent('btnFullscreen', 'click', basculerPleinEcran);\n"
AJOUT_EVT = "    onEvent('btnFullscreen', 'click', basculerPleinEcran);\n    onEvent('btnTogglePanneauDroit', 'click', basculerPanneauDroit);\n"
if "btnTogglePanneauDroit', 'click'" in texte:
    pass
elif ANCRE_EVT not in texte:
    erreurs.append("ANCRE_EVT introuvable")
else:
    texte = texte.replace(ANCRE_EVT, AJOUT_EVT, 1)

# ---------------------------------------------------------------------
if erreurs:
    print("ECHEC : rien n'a ete modifie. Ancre(s) introuvable(s) :")
    for e in erreurs:
        print("  -", e)
    raise SystemExit(1)

if texte == original:
    print("Deja applique : aucun changement necessaire.")
else:
    CHEMIN.write_text(texte, encoding="utf-8")
    print("OK : geoportail_admin.html mis a jour (bouton panneau droit).")