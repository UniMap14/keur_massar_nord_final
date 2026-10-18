# -*- coding: utf-8 -*-
"""
Corrige 2 coquilles (espaces manquants) dans les explications existantes,
et fixe un ordre d'affichage narratif explicite (actuellement tout est a
ordre=0, donc l'affichage depend du hasard des dates d'ajout).

Idempotent : si le texte est deja corrige / l'ordre deja fixe, le script
le signale sans rien casser.
"""
from foncier.models import CarteThematique

# On repere les cartes par mot-cle dans le titre plutot que par id en dur,
# pour que le script reste correct meme si les id different de ce qu'on a vu.
ORDRE_NARRATIF = [
    ("pente", 1),               # relief / contexte physique d'abord
    ("drainage", 2),             # hydrologie
    ("densité des infrastructures", 3),   # vue d'ensemble des équipements
    ("établissements scolaires", 4),      # équipement : éducation
    ("structures de santé", 5),           # équipement : santé
]

cartes = list(CarteThematique.objects.all())
print(f"{len(cartes)} carte(s) trouvee(s).\n")

# --- 1) Corrections de texte (espaces manquants) ---
for c in cartes:
    texte = c.explication
    nouveau_texte = texte

    if "apparaissentponctuellement" in nouveau_texte:
        nouveau_texte = nouveau_texte.replace(
            "apparaissentponctuellement", "apparaissent ponctuellement"
        )
    if "territoirecommunal" in nouveau_texte:
        nouveau_texte = nouveau_texte.replace(
            "territoirecommunal", "territoire communal"
        )

    if nouveau_texte != texte:
        c.explication = nouveau_texte
        c.save(update_fields=["explication"])
        print(f"OK texte corrige : id={c.id} ({c.titre})")
    else:
        print(f"IGNORE (deja propre) : id={c.id} ({c.titre})")

# --- 2) Ordre d'affichage narratif ---
print()
for mot_cle, ordre in ORDRE_NARRATIF:
    match = [c for c in cartes if mot_cle.lower() in c.titre.lower()]
    if not match:
        print(f"ATTENTION : aucune carte ne correspond a '{mot_cle}', ignore.")
        continue
    for c in match:
        if c.ordre != ordre:
            c.ordre = ordre
            c.save(update_fields=["ordre"])
            print(f"OK ordre={ordre} applique : id={c.id} ({c.titre})")
        else:
            print(f"IGNORE (ordre deja {ordre}) : id={c.id} ({c.titre})")

print("\nTermine.")