import sys

FICHIERS = [
    "foncier/templates/foncier/geoportail.html",
    "foncier/templates/foncier/geoportail_admin.html",
]

ancien = '''    coucheRayon = L.circle(centre, { radius: rayon, color: '#c9982e', weight: 2, fillColor: '#c9982e', fillOpacity: 0.12 }).addTo(map);'''
nouveau = '''    coucheRayon = L.circle(centre, { radius: rayon, color: '#b23b2e', weight: 2.5, fillColor: '#b23b2e', fillOpacity: 0.15 }).addTo(map);'''

# Variante avec mise en forme multi-lignes (au cas ou)
ancien_multiligne = '''    coucheRayon = L.circle(centre, {
      radius: rayon,
      color: '#c9982e',
      weight: 2,
      fillColor: '#c9982e',
      fillOpacity: 0.12,
    }).addTo(map);'''
nouveau_multiligne = '''    coucheRayon = L.circle(centre, {
      radius: rayon,
      color: '#b23b2e',
      weight: 2.5,
      fillColor: '#b23b2e',
      fillOpacity: 0.15,
    }).addTo(map);'''

for chemin in FICHIERS:
    try:
        with open(chemin, encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"IGNORE : {chemin} introuvable.")
        continue

    if "color: '#b23b2e', weight: 2.5, fillColor: '#b23b2e'" in contenu or "color: '#b23b2e',\n      weight: 2.5" in contenu:
        print(f"DEJA FAIT : {chemin} deja en rouge.")
    elif ancien in contenu:
        contenu = contenu.replace(ancien, nouveau, 1)
        with open(chemin, "w", encoding="utf-8", newline="") as f:
            f.write(contenu)
        print(f"OK : {chemin} - cercle de rayon passe en rouge.")
    elif ancien_multiligne in contenu:
        contenu = contenu.replace(ancien_multiligne, nouveau_multiligne, 1)
        with open(chemin, "w", encoding="utf-8", newline="") as f:
            f.write(contenu)
        print(f"OK : {chemin} - cercle de rayon passe en rouge (variante multi-ligne).")
    else:
        print(f"ERREUR : bloc du cercle introuvable dans {chemin}.")