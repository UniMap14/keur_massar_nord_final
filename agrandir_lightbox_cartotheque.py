# -*- coding: utf-8 -*-
"""
A lancer depuis la racine du projet (ou se trouve manage.py) :

    python agrandir_lightbox_cartotheque.py

Fait en sorte que l'image de la carte, en plein ecran, occupe presque tout
l'espace disponible (largeur ET hauteur), au lieu de rester petite avec
un grand espace noir vide a cote.
"""
import io

chemin = "foncier/templates/foncier/cartotheque.html"

edits = []

edits.append((
"""    .carto-lightbox-img-wrap{ max-width:1300px; width:100%; text-align:center; }
    .carto-lightbox-img-wrap img{
        max-width:100%; max-height:84vh; border-radius:10px; cursor:zoom-in;
        box-shadow: 0 30px 70px rgba(0,0,0,.5);
    }
    .carto-lightbox-caption{ color:#fff; font-size:14.5px; font-weight:600; margin-top:18px; }""",
"""    .carto-lightbox-img-wrap{
        width:94vw; height:88vh; max-width:none;
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        gap:14px;
    }
    .carto-lightbox-img-wrap img{
        max-width:100%; max-height:100%; width:auto; height:auto; object-fit:contain;
        border-radius:10px; cursor:zoom-in;
        box-shadow: 0 30px 70px rgba(0,0,0,.5);
    }
    .carto-lightbox-caption{ color:#fff; font-size:14.5px; font-weight:600; margin-top:0; }"""
))


def lire(c):
    with io.open(c, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(c, contenu):
    with io.open(c, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)


contenu = lire(chemin)
erreurs = []
for i, (old, new) in enumerate(edits):
    n = contenu.count(old)
    if n != 1:
        erreurs.append(f"modification #{i + 1}: trouve {n} fois (attendu 1)")

if erreurs:
    print("ECHEC - AUCUNE modification appliquee (fichier inchange). Problemes :")
    for e in erreurs:
        print(" -", e)
    print("\nEnvoyez-moi l'extrait exact concerne pour que j'ajuste l'ancre.")
else:
    for old, new in edits:
        contenu = contenu.replace(old, new)
    ecrire(chemin, contenu)
    print("OK - la lightbox occupe maintenant presque tout l'ecran.")
    print("Rechargez la page (Ctrl+F5) pour voir le resultat.")