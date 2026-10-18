# -*- coding: utf-8 -*-
"""
Ajoute un bouton de telechargement dans la lightbox plein ecran de la
page Galerie, a cote du bouton fermer. Au clic, l'utilisateur telecharge
la photo actuellement affichee en grand.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/galerie.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

# 1) CSS du bouton telechargement
ANCIEN_CSS = '''    .gal-lightbox-close:hover{ background: var(--gp-gold); color: var(--gp-brown-dark); }'''

NOUVEAU_CSS = '''    .gal-lightbox-close:hover{ background: var(--gp-gold); color: var(--gp-brown-dark); }
    .gal-lightbox-download{
        position:absolute; top:24px; left:24px; z-index:2;
        width:42px; height:42px; border-radius:50%; border:none;
        background:rgba(255,255,255,.12); color:#fff; font-size:16px; cursor:pointer;
        display:flex; align-items:center; justify-content:center;
        text-decoration:none;
        transition: background .2s ease;
    }
    .gal-lightbox-download:hover{ background: var(--gp-gold); color: var(--gp-brown-dark); }
    @media (max-width: 700px){
        .gal-lightbox-download{ top:14px; left:14px; width:38px; height:38px; font-size:13px; }
    }'''

if '.gal-lightbox-download{' in contenu:
    pass
elif ANCIEN_CSS not in contenu:
    erreurs.append("ancre CSS introuvable (.gal-lightbox-close:hover)")
else:
    contenu = contenu.replace(ANCIEN_CSS, NOUVEAU_CSS, 1)
    remplacements_ok += 1

# 2) Bouton dans le HTML de la lightbox
ANCIEN_HTML = '''    <button type="button" class="gal-lightbox-close" id="galLightboxClose" aria-label="Fermer"><i class="fa-solid fa-xmark"></i></button>'''

NOUVEAU_HTML = '''    <a href="#" class="gal-lightbox-download" id="galLightboxDownload" download aria-label="T&eacute;l&eacute;charger l'image"><i class="fa-solid fa-download"></i></a>
    <button type="button" class="gal-lightbox-close" id="galLightboxClose" aria-label="Fermer"><i class="fa-solid fa-xmark"></i></button>'''

if 'id="galLightboxDownload"' in contenu:
    pass
elif ANCIEN_HTML not in contenu:
    erreurs.append("ancre HTML introuvable (bouton Fermer de la lightbox)")
else:
    contenu = contenu.replace(ANCIEN_HTML, NOUVEAU_HTML, 1)
    remplacements_ok += 1

# 3) JS : recuperer le bouton + mettre a jour son href/download a chaque affichage
ANCIEN_JS_CONST = '''    const btnFermer = document.getElementById('galLightboxClose');'''

NOUVEAU_JS_CONST = '''    const btnFermer = document.getElementById('galLightboxClose');
    const btnTelecharger = document.getElementById('galLightboxDownload');'''

if "getElementById('galLightboxDownload')" in contenu:
    pass
elif ANCIEN_JS_CONST not in contenu:
    erreurs.append("ancre JS introuvable (const btnFermer)")
else:
    contenu = contenu.replace(ANCIEN_JS_CONST, NOUVEAU_JS_CONST, 1)
    remplacements_ok += 1

ANCIEN_JS_AFFICHER = '''        compteur.textContent = (indexActuel + 1) + ' / ' + cartes.length;
    }'''

NOUVEAU_JS_AFFICHER = '''        compteur.textContent = (indexActuel + 1) + ' / ' + cartes.length;
        const nomFichier = (carte.getAttribute('data-caption') || 'photo').trim().replace(/[^\\w\\-]+/g, '_');
        btnTelecharger.href = carte.getAttribute('data-src');
        btnTelecharger.setAttribute('download', nomFichier + '.jpg');
    }'''

if "btnTelecharger.href = carte.getAttribute('data-src');" in contenu:
    pass
elif ANCIEN_JS_AFFICHER not in contenu:
    erreurs.append("ancre JS introuvable (fin de la fonction afficher())")
else:
    contenu = contenu.replace(ANCIEN_JS_AFFICHER, NOUVEAU_JS_AFFICHER, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")