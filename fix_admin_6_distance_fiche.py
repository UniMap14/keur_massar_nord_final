# -*- coding: utf-8 -*-
"""
ADMIN - Feature 6/6 : distance (par rapport a la position de
l'utilisateur) dans la fiche parcelle.

Idempotent.
"""
import io

chemin = "foncier/templates/foncier/geoportail_admin.html"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "fpDistanceTexte"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
else:
    # --- 1) Calcul de la distance, juste apres "const p = feature.properties;" ---
    ancien_debut = '''  function contenuFicheParcelle(feature) {
    const p = feature.properties;
'''
    if ancien_debut not in contenu:
        raise SystemExit("ANCRE debut contenuFicheParcelle INTROUVABLE - abandon, rien n'a ete modifie.")
    nouveau_debut = '''  function contenuFicheParcelle(feature) {
    const p = feature.properties;

    let fpDistanceTexte = '';
    if (userLatLng) {
      const centreFiche = L.geoJSON(feature).getBounds().getCenter();
      const fpDist = L.latLng(userLatLng[0], userLatLng[1]).distanceTo(centreFiche);
      fpDistanceTexte = fpDist >= 1000 ? (fpDist / 1000).toFixed(2) + ' km' : Math.round(fpDist) + ' m';
    }
'''
    contenu = contenu.replace(ancien_debut, nouveau_debut)

    # --- 2) Ligne fp-row distance, juste apres la ligne Secteur ---
    ancien_ligne = '''      (p.adresse_parcelle ? '<div class="fp-row"><span class="fp-label">Secteur</span><span class="fp-value">' + p.adresse_parcelle + '</span></div>' : '') +
      champsAdmin +'''
    if ancien_ligne not in contenu:
        raise SystemExit("ANCRE ligne Secteur INTROUVABLE - abandon partiel, verifie le fichier.")
    nouveau_ligne = '''      (p.adresse_parcelle ? '<div class="fp-row"><span class="fp-label">Secteur</span><span class="fp-value">' + p.adresse_parcelle + '</span></div>' : '') +
      (fpDistanceTexte ? '<div class="fp-row"><span class="fp-label">Distance (votre position)</span><span class="fp-value">' + fpDistanceTexte + '</span></div>' : '') +
      champsAdmin +'''
    contenu = contenu.replace(ancien_ligne, nouveau_ligne)

    with io.open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("Patch applique avec succes (feature 6/6 : distance dans la fiche parcelle).")