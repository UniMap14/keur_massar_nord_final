# -*- coding: utf-8 -*-
"""
Quand un seul resultat est visible dans la Cartotheque (apres filtre ou
recherche), cette carte s'affiche en grand format pleine largeur
(image + texte cote a cote) au lieu d'une petite case de grille.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/cartotheque.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

if '.carto-card-full{' in contenu:
    print("OK : deja applique, rien a faire.")
else:
    erreurs = []
    remplacements_ok = 0

    def remplacer(ancien, nouveau):
        global contenu, remplacements_ok
        if ancien not in contenu:
            erreurs.append(f"ancre introuvable : {ancien[:70]}...")
            return
        contenu = contenu.replace(ancien, nouveau, 1)
        remplacements_ok += 1

    # 1) CSS : format "carte unique pleine largeur"
    remplacer(
        '''    @media (max-width: 860px){
        .carto-list{ grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:20px; }
    }
    @media (max-width: 520px){
        .carto-list{ grid-template-columns: 1fr; }
    }''',
        '''    .carto-card.carto-card-full{
        grid-column: 1 / -1;
        display:grid; grid-template-columns: 1.1fr 1fr;
    }
    .carto-card.carto-card-full .carto-card-img{ aspect-ratio:auto; min-height:360px; }
    .carto-card.carto-card-full .carto-card-body{ justify-content:center; padding:40px 48px; }
    .carto-card.carto-card-full .carto-card-body h3{ font-size:24px; }
    .carto-card.carto-card-full .carto-card-body p{
        -webkit-line-clamp:unset; display:block; overflow:visible; font-size:15px; line-height:1.75;
    }

    @media (max-width: 860px){
        .carto-list{ grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:20px; }
        .carto-card.carto-card-full{ grid-template-columns: 1fr; }
        .carto-card.carto-card-full .carto-card-img{ min-height:240px; }
        .carto-card.carto-card-full .carto-card-body{ padding:26px 24px; }
    }
    @media (max-width: 520px){
        .carto-list{ grid-template-columns: 1fr; }
    }''',
    )

    # 2) JS : basculer la classe carto-card-full selon le nombre de resultats visibles
    remplacer(
        '''        if (boutonEffacer) boutonEffacer.classList.toggle('visible', requete !== '');

        const filtreActif = requete !== '' || themeActif !== '';''',
        '''        toutesLesCartes.forEach(function (carte) { carte.classList.remove('carto-card-full'); });
        if (visibles === 1) {
            const carteUnique = toutesLesCartes.find(function (carte) { return !carte.classList.contains('carto-hidden'); });
            if (carteUnique) carteUnique.classList.add('carto-card-full');
        }

        if (boutonEffacer) boutonEffacer.classList.toggle('visible', requete !== '');

        const filtreActif = requete !== '' || themeActif !== '';''',
    )

    if erreurs:
        print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
        for e in erreurs:
            print(" -", e)
    else:
        with open(CHEMIN, "w", encoding="utf-8") as f:
            f.write(contenu)
        print(f"OK : {remplacements_ok} modification(s) appliquee(s).")