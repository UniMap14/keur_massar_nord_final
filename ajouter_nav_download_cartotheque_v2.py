# -*- coding: utf-8 -*-
"""
A lancer depuis la racine du projet (ou se trouve manage.py) :

    python ajouter_nav_download_cartotheque_v2.py

Version corrigee (indentation exacte confirmee par repr()).
"""
import io

chemin = "foncier/templates/foncier/cartotheque.html"

edits = []

# 1) CSS
edits.append((
"""    .carto-lightbox-close:hover{ background: var(--cp-gold); color: var(--cp-brown-dark); }
    .carto-lightbox-img-wrap{ max-width:1300px; width:100%; text-align:center; }""",
"""    .carto-lightbox-close:hover{ background: var(--cp-gold); color: var(--cp-brown-dark); }
    .carto-lightbox-download{
        position:absolute; top:24px; right:78px; z-index:2;
        width:42px; height:42px; border-radius:50%; border:none;
        background:rgba(255,255,255,.12); color:#fff; font-size:16px; cursor:pointer;
        display:flex; align-items:center; justify-content:center; transition: background .2s ease;
        text-decoration:none;
    }
    .carto-lightbox-download:hover{ background: var(--cp-gold); color: var(--cp-brown-dark); }
    .carto-lightbox-nav{
        position:absolute; top:50%; transform:translateY(-50%); z-index:2;
        width:52px; height:52px; border-radius:50%; border:none;
        background:rgba(255,255,255,.12); color:#fff; font-size:20px; cursor:pointer;
        display:flex; align-items:center; justify-content:center; transition: background .2s ease;
    }
    .carto-lightbox-nav:hover{ background: var(--cp-gold); color: var(--cp-brown-dark); }
    .carto-lightbox-nav:disabled{ opacity:.3; cursor:default; }
    .carto-lightbox-nav:disabled:hover{ background:rgba(255,255,255,.12); color:#fff; }
    .carto-lightbox-prev{ left:24px; }
    .carto-lightbox-next{ right:24px; }
    @media (max-width: 700px){
        .carto-lightbox-nav{ width:42px; height:42px; font-size:16px; }
        .carto-lightbox-download{ right:70px; }
    }
    .carto-lightbox-img-wrap{ max-width:1300px; width:100%; text-align:center; }"""
))

# 2) HTML
edits.append((
"""<div class="carto-lightbox-overlay" id="cartoLightbox">
    <button type="button" class="carto-lightbox-close" id="cartoLightboxClose" aria-label="Fermer"><i class="fa-solid fa-xmark"></i></button>
    <div class="carto-lightbox-img-wrap">""",
"""<div class="carto-lightbox-overlay" id="cartoLightbox">
    <button type="button" class="carto-lightbox-close" id="cartoLightboxClose" aria-label="Fermer"><i class="fa-solid fa-xmark"></i></button>
    <a href="#" class="carto-lightbox-download" id="cartoLightboxDownload" download aria-label="Télécharger"><i class="fa-solid fa-download"></i></a>
    <button type="button" class="carto-lightbox-nav carto-lightbox-prev" id="cartoLightboxPrev" aria-label="Carte précédente"><i class="fa-solid fa-chevron-left"></i></button>
    <button type="button" class="carto-lightbox-nav carto-lightbox-next" id="cartoLightboxNext" aria-label="Carte suivante"><i class="fa-solid fa-chevron-right"></i></button>
    <div class="carto-lightbox-img-wrap">"""
))

# 3) JS
edits.append((
"""    cartes.forEach(function (carte) {
        carte.addEventListener('click', function () {
            img.src = carte.getAttribute('data-src');
            img.alt = carte.getAttribute('data-caption');
            caption.textContent = carte.getAttribute('data-caption');
            overlay.classList.add('open');
        });
    });

    btnFermer.addEventListener('click', function () { overlay.classList.remove('open'); });
    overlay.addEventListener('click', function (e) { if (e.target === overlay) overlay.classList.remove('open'); });
    document.addEventListener('keydown', function (e) {
        if (!overlay.classList.contains('open')) return;
        if (e.key === 'Escape') overlay.classList.remove('open');
    });""",
"""    const btnDownload = document.getElementById('cartoLightboxDownload');
    const btnPrev = document.getElementById('cartoLightboxPrev');
    const btnNext = document.getElementById('cartoLightboxNext');
    let indexActuel = 0;

    function ouvrirCarte(indice) {
        if (indice < 0 || indice >= cartes.length) return;
        indexActuel = indice;
        const carte = cartes[indexActuel];
        const src = carte.getAttribute('data-src');
        const legende = carte.getAttribute('data-caption') || 'carte';
        img.src = src;
        img.alt = legende;
        caption.textContent = legende;
        if (btnDownload) {
            btnDownload.href = src;
            btnDownload.setAttribute('download', legende.replace(/[^a-z0-9_\\-]+/gi, '_') + '.jpg');
        }
        if (btnPrev) btnPrev.disabled = (indexActuel === 0);
        if (btnNext) btnNext.disabled = (indexActuel === cartes.length - 1);
        overlay.classList.add('open');
    }

    cartes.forEach(function (carte, indice) {
        carte.addEventListener('click', function () { ouvrirCarte(indice); });
    });

    if (btnPrev) btnPrev.addEventListener('click', function (e) { e.stopPropagation(); ouvrirCarte(indexActuel - 1); });
    if (btnNext) btnNext.addEventListener('click', function (e) { e.stopPropagation(); ouvrirCarte(indexActuel + 1); });

    btnFermer.addEventListener('click', function () { overlay.classList.remove('open'); });
    overlay.addEventListener('click', function (e) { if (e.target === overlay) overlay.classList.remove('open'); });
    document.addEventListener('keydown', function (e) {
        if (!overlay.classList.contains('open')) return;
        if (e.key === 'Escape') overlay.classList.remove('open');
        if (e.key === 'ArrowLeft') ouvrirCarte(indexActuel - 1);
        if (e.key === 'ArrowRight') ouvrirCarte(indexActuel + 1);
    });"""
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
    print("OK - toutes les modifications appliquees a cartotheque.html.")
    print("Rechargez la page (Ctrl+F5) pour voir le bouton de telechargement et les fleches.")