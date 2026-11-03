# -*- coding: utf-8 -*-
"""
Quand on clique sur une infrastructure dans la liste "Infrastructures
dans la zone" (resultat de la selection spatiale), un marqueur rouge
apparait sur la carte a son emplacement exact, et la carte zoome
dessus -- comme la selection d'une entite ponctuelle dans QGIS.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "surlignerInfrastructure"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Variable globale pour le marqueur de surlignage ---
    ancienne_var = "  let selectionInfra = [];"
    if ancienne_var not in contenu:
        raise SystemExit("ANCRE 'selectionInfra' INTROUVABLE - abandon, rien n'a ete modifie.")
    nouvelle_var = ancienne_var + "\n  let coucheInfraSurlignee = null;"
    contenu = contenu.replace(ancienne_var, nouvelle_var)

    # --- 2) Liste infra : ajoute data-lat/data-lng + gestionnaire de clic ---
    ancienne_liste = '''    const sectionInfra = document.getElementById('selInfraSection');
    const listeInfra = document.getElementById('selInfraListe');
    if (sectionInfra && listeInfra) {
      if (selectionInfra.length) {
        listeInfra.innerHTML = selectionInfra.map(function (i) {
          return '<div class="geo-selection-item"><span class="nom">' + echapperHtml(i.nom || 'Infrastructure') + '</span></div>';
        }).join('');
        sectionInfra.style.display = 'block';
      } else {
        listeInfra.innerHTML = '';
        sectionInfra.style.display = 'none';
      }
    }'''
    if ancienne_liste not in contenu:
        raise SystemExit("ANCRE liste infra INTROUVABLE - abandon partiel, verifie le fichier.")

    nouvelle_liste = '''    const sectionInfra = document.getElementById('selInfraSection');
    const listeInfra = document.getElementById('selInfraListe');
    if (sectionInfra && listeInfra) {
      if (selectionInfra.length) {
        listeInfra.innerHTML = selectionInfra.map(function (i) {
          return '<div class="geo-selection-item" data-lat="' + i.latitude + '" data-lng="' + i.longitude + '"><span class="nom">' + echapperHtml(i.nom || 'Infrastructure') + '</span></div>';
        }).join('');
        sectionInfra.style.display = 'block';
        listeInfra.querySelectorAll('.geo-selection-item').forEach(function (el) {
          el.style.cursor = 'pointer';
          el.addEventListener('click', function () {
            const lat = parseFloat(el.getAttribute('data-lat'));
            const lng = parseFloat(el.getAttribute('data-lng'));
            surlignerInfrastructure(lat, lng);
          });
        });
      } else {
        listeInfra.innerHTML = '';
        sectionInfra.style.display = 'none';
      }
    }'''
    contenu = contenu.replace(ancienne_liste, nouvelle_liste)

    # --- 3) Fonction de surlignage, juste avant effacerSelection ---
    ancre_fonction = "  function effacerSelection() {"
    if ancre_fonction not in contenu:
        raise SystemExit("ANCRE 'function effacerSelection' INTROUVABLE - abandon partiel, verifie le fichier.")

    nouvelle_fonction = '''  function surlignerInfrastructure(lat, lng) {
    if (isNaN(lat) || isNaN(lng)) return;
    if (coucheInfraSurlignee) { map.removeLayer(coucheInfraSurlignee); coucheInfraSurlignee = null; }
    coucheInfraSurlignee = L.circleMarker([lat, lng], {
      radius: 10,
      color: '#ffffff',
      weight: 2,
      fillColor: '#d12f2f',
      fillOpacity: 0.95
    }).addTo(map);
    map.flyTo([lat, lng], Math.max(map.getZoom(), 18));
  }

'''
    contenu = contenu.replace(ancre_fonction, nouvelle_fonction + ancre_fonction)

    # --- 4) effacerSelection : retire aussi le marqueur rouge ---
    ancien_effacer = '''    formeSelectionActuelle = null;
    selectionZones = [];
    selectionInfra = [];'''
    if ancien_effacer not in contenu:
        raise SystemExit("ANCRE effacerSelection (reset) INTROUVABLE - abandon partiel, verifie le fichier.")
    nouvel_effacer = ancien_effacer + '''
    if (coucheInfraSurlignee) { map.removeLayer(coucheInfraSurlignee); coucheInfraSurlignee = null; }'''
    contenu = contenu.replace(ancien_effacer, nouvel_effacer)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes.")