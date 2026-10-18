# -*- coding: utf-8 -*-
"""
Round 23 (home.html) : rend chaque panneau du tableau de bord
cliquable/agrandissable (surtout utile pour les graphiques et la
mini-carte, trop petits dans leur tuile compacte). Un clic sur
l'en-tete du panneau l'agrandit en superposition plein ecran ; un
second clic, un clic sur l'arriere-plan assombri, ou Echap le
referme. Les instances Chart.js et la carte Leaflet sont
redimensionnees a chaque ouverture/fermeture pour rester nettes.

Idempotent. Ancres 100% ASCII.
"""
import pathlib

CHEMIN = pathlib.Path("foncier/templates/dashboard/home.html")

texte = CHEMIN.read_text(encoding="utf-8")
original = texte
erreurs = []

# ---------------------------------------------------------------------
# 1) CSS : panneau agrandi + fond assombri
# ---------------------------------------------------------------------
ANCRE_CSS = """    .panel,
    .kpi-card {
        box-shadow: 0 1px 3px rgba(42,38,32,0.06) !important;
        border: 1px solid rgba(42,38,32,0.07) !important;
    }"""
AJOUT_CSS = """    .panel,
    .kpi-card {
        box-shadow: 0 1px 3px rgba(42,38,32,0.06) !important;
        border: 1px solid rgba(42,38,32,0.07) !important;
    }

    /* ===== Panneaux agrandissables au clic (round 23) ===== */
    .panel-expand-overlay {
        position: fixed;
        inset: 0;
        background: rgba(20,15,10,0.55);
        z-index: 999;
    }
    .dashboard-grid .panel-header:hover {
        background: rgba(42,38,32,0.04);
    }
    .dashboard-grid .panel.expanded {
        position: fixed !important;
        top: 6vh !important;
        left: 6vw !important;
        right: 6vw !important;
        bottom: 6vh !important;
        width: auto !important;
        height: auto !important;
        z-index: 1000 !important;
        box-shadow: 0 24px 64px rgba(0,0,0,0.35) !important;
        overflow: auto !important;
    }
    .dashboard-grid .panel.expanded .panel-body,
    .dashboard-grid .panel.expanded .panel-body.flush {
        height: calc(100% - 50px) !important;
        max-height: none !important;
    }
    .dashboard-grid .panel.expanded .chart-wrap,
    .dashboard-grid .panel.expanded .chart-wrap-sm,
    .dashboard-grid .panel.expanded .mini-map-canvas {
        height: 70% !important;
    }"""
if "Panneaux agrandissables au clic (round 23)" in texte:
    pass
elif ANCRE_CSS not in texte:
    erreurs.append("ANCRE_CSS introuvable")
else:
    texte = texte.replace(ANCRE_CSS, AJOUT_CSS, 1)

# ---------------------------------------------------------------------
# 2) JS : logique d'ouverture/fermeture + redimensionnement
# ---------------------------------------------------------------------
ANCRE_JS = """        L.marker([14.79, -17.31]).addTo(miniMap).bindPopup('Keur Massar Nord');
    }
});
</script>
{% endblock %}"""
AJOUT_JS = """        L.marker([14.79, -17.31]).addTo(miniMap).bindPopup('Keur Massar Nord');
    }

    // ===== Panneaux cliquables / agrandissables (round 23) =====
    var overlayExpansion = document.createElement('div');
    overlayExpansion.className = 'panel-expand-overlay';
    overlayExpansion.style.display = 'none';
    document.body.appendChild(overlayExpansion);

    function redimensionnerGraphiques() {
        if (window.Chart && Chart.instances) {
            Object.values(Chart.instances).forEach(function (inst) { inst.resize(); });
        }
        if (typeof miniMap !== 'undefined' && miniMap) {
            miniMap.invalidateSize();
        }
    }

    function fermerExpansion() {
        var ouvert = document.querySelector('.panel.expanded');
        if (ouvert) { ouvert.classList.remove('expanded'); }
        overlayExpansion.style.display = 'none';
        setTimeout(redimensionnerGraphiques, 50);
    }

    overlayExpansion.addEventListener('click', fermerExpansion);
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { fermerExpansion(); }
    });

    document.querySelectorAll('.dashboard-grid .panel-header').forEach(function (header) {
        header.style.cursor = 'zoom-in';
        header.addEventListener('click', function (e) {
            if (e.target.closest('a') || e.target.closest('button')) { return; }
            var panel = header.closest('.panel');
            if (!panel) { return; }
            var dejaOuvert = panel.classList.contains('expanded');
            document.querySelectorAll('.panel.expanded').forEach(function (p) { p.classList.remove('expanded'); });
            if (dejaOuvert) {
                overlayExpansion.style.display = 'none';
            } else {
                panel.classList.add('expanded');
                overlayExpansion.style.display = 'block';
            }
            setTimeout(redimensionnerGraphiques, 50);
        });
    });
});
</script>
{% endblock %}"""
if "Panneaux cliquables / agrandissables (round 23)" in texte:
    pass
elif ANCRE_JS not in texte:
    erreurs.append("ANCRE_JS introuvable")
else:
    texte = texte.replace(ANCRE_JS, AJOUT_JS, 1)

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
    print("OK : dashboard/home.html -- round 23 (panneaux cliquables/agrandissables).")