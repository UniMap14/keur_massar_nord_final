CHEMIN = "foncier/templates/dashboard/home.html"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

resultats = []

# --- 1. CSS de la tuile Geoportail ---
MARQUEUR_CSS = ".geo-access-card {"

ancien_css = '''    @media (prefers-reduced-motion: reduce) {
        .kpi-card, .panel, .recouvrement-bar-fill::after {
            animation: none !important;
            opacity: 1 !important;
            transform: none !important;
        }
    }
</style>'''

nouveau_css = '''    /* ===== Tuile d'acces au Geoportail (mise en avant) ===== */
    .geo-access-card {
        grid-column: 1 / -1;
        background: linear-gradient(135deg, #3c2a20 0%, #1a100b 100%);
        border-radius: 14px;
        padding: 26px 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        flex-wrap: wrap;
        text-decoration: none;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(201,152,46,.35);
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .geo-access-card::before {
        content: "";
        position: absolute; inset: 0;
        background-image:
            linear-gradient(rgba(201,152,46,.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(201,152,46,.08) 1px, transparent 1px);
        background-size: 30px 30px;
    }
    .geo-access-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 34px -10px rgba(0,0,0,.4);
    }
    .geo-access-left {
        position: relative; z-index: 1;
        display: flex; align-items: center; gap: 18px;
    }
    .geo-access-icon {
        width: 52px; height: 52px; border-radius: 14px; flex-shrink: 0;
        background: linear-gradient(135deg, #e0b854, #c9982e);
        display: flex; align-items: center; justify-content: center;
        font-size: 21px; color: #3c2a20;
        box-shadow: 0 6px 14px rgba(201,152,46,.3);
    }
    .geo-access-text h3 {
        font-size: 16.5px; font-weight: 700; color: #fff; margin: 0 0 4px;
    }
    .geo-access-text p {
        font-size: 12.5px; color: rgba(255,255,255,.7); margin: 0;
    }
    .geo-access-btn {
        position: relative; z-index: 1;
        display: inline-flex; align-items: center; gap: 9px;
        background: linear-gradient(135deg, #e0b854, #c9982e);
        color: #3c2a20; font-weight: 700; font-size: 13.5px;
        padding: 12px 22px; border-radius: 999px; white-space: nowrap;
        transition: box-shadow .2s ease;
    }
    .geo-access-card:hover .geo-access-btn {
        box-shadow: 0 8px 18px rgba(201,152,46,.4);
    }

    @media (prefers-reduced-motion: reduce) {
        .kpi-card, .panel, .recouvrement-bar-fill::after {
            animation: none !important;
            opacity: 1 !important;
            transform: none !important;
        }
    }
</style>'''

if MARQUEUR_CSS in contenu:
    resultats.append("IGNORE : CSS de la tuile deja present.")
elif ancien_css in contenu:
    contenu = contenu.replace(ancien_css, nouveau_css, 1)
    resultats.append("OK : CSS de la tuile Geoportail ajoute.")
else:
    resultats.append("ERREUR : bloc CSS ancre introuvable.")

# --- 2. HTML de la tuile, tout en haut de la grille KPI ---
MARQUEUR_HTML = "class=\"geo-access-card\">"

ancien_html = '''<div class="kpi-grid">
{% if peut_fiscal %}'''

nouveau_html = '''<a href="{% url 'geoportail_admin' %}" class="geo-access-card">
  <div class="geo-access-left">
    <div class="geo-access-icon"><i class="fa-solid fa-map-location-dot"></i></div>
    <div class="geo-access-text">
      <h3>Geoportail SIG</h3>
      <p>Carte cadastrale complete, outils SIG et edition des parcelles en plein ecran.</p>
    </div>
  </div>
  <span class="geo-access-btn">Acceder au Geoportail <i class="fa-solid fa-arrow-right"></i></span>
</a>

<div class="kpi-grid">
{% if peut_fiscal %}'''

if MARQUEUR_HTML in contenu:
    resultats.append("IGNORE : bouton Geoportail deja present.")
elif ancien_html in contenu:
    contenu = contenu.replace(ancien_html, nouveau_html, 1)
    resultats.append("OK : bouton 'Acceder au Geoportail' ajoute en haut du tableau de bord.")
else:
    resultats.append("ERREUR : bloc HTML ancre introuvable.")

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

print("\n".join(resultats))