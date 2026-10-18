# -*- coding: utf-8 -*-
"""
Remplace les boutons-filtres (chips) de la Cartotheque par un menu
deroulant (select) pour choisir le theme.

Idempotent.
"""
CHEMIN = "foncier/templates/foncier/cartotheque.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

if 'id="cartoFiltreSelect"' in contenu:
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

    # 1) CSS : style du menu deroulant (remplace le style des chips)
    remplacer(
        '''    .carto-filtres{ display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-top:6px; }
    .carto-filtre-chip{
        border:1.5px solid var(--cp-border); background:#fff; color:var(--cp-brown-light);
        font-size:12.5px; font-weight:700; padding:7px 15px; border-radius:999px; cursor:pointer;
        transition: all .15s ease;
    }
    .carto-filtre-chip:hover{ background:var(--cp-cream-2); }
    .carto-filtre-chip.active{ background:var(--cp-brown-dark); border-color:var(--cp-brown-dark); color:#fff; }''',
        '''    .carto-filtre-select{
        width:100%; max-width:320px; margin-top:6px; padding:12px 40px 12px 18px; border-radius:999px;
        border:1px solid var(--cp-border); background-color:#fff; color:var(--cp-brown-dark);
        font-size:14px; font-weight:600; cursor:pointer; appearance:none; -webkit-appearance:none;
        background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='8'><path d='M1 1l5 5 5-5' stroke='%235a3d2c' stroke-width='1.6' fill='none' stroke-linecap='round' stroke-linejoin='round'/></svg>");
        background-repeat:no-repeat; background-position:right 16px center;
        box-shadow:0 2px 10px rgba(43,27,20,.05);
        transition: border-color .2s ease, box-shadow .2s ease;
    }
    .carto-filtre-select:focus{ outline:none; border-color:var(--cp-gold); box-shadow:0 0 0 3px rgba(217,165,43,.18); }''',
    )

    # 2) HTML : menu deroulant a la place des boutons
    remplacer(
        '''        <div class="carto-filtres" id="cartoFiltres">
            <button type="button" class="carto-filtre-chip" data-theme-filtre="">Toutes</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Relief &amp; pentes">Relief &amp; pentes</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Hydrologie">Hydrologie</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Infrastructures">Infrastructures</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="\u00c9ducation">\u00c9ducation</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Sant\u00e9">Sant\u00e9</button>
            <button type="button" class="carto-filtre-chip" data-theme-filtre="Analyse territoriale">Analyse territoriale</button>
        </div>''',
        '''        <select class="carto-filtre-select" id="cartoFiltreSelect">
            <option value="" disabled selected>Choisir un filtre...</option>
            <option value="__TOUTES__">Toutes les cartes</option>
            <option value="Relief &amp; pentes">Relief &amp; pentes</option>
            <option value="Hydrologie">Hydrologie</option>
            <option value="Infrastructures">Infrastructures</option>
            <option value="\u00c9ducation">\u00c9ducation</option>
            <option value="Sant\u00e9">Sant\u00e9</option>
            <option value="Analyse territoriale">Analyse territoriale</option>
        </select>''',
    )

    # 3) JS : reference au select au lieu des chips
    remplacer(
        '''    const chipsFiltre = document.querySelectorAll('.carto-filtre-chip');
    const messageChoisirFiltre = document.getElementById('cartoChoisirFiltre');''',
        '''    const selectFiltre = document.getElementById('cartoFiltreSelect');
    const messageChoisirFiltre = document.getElementById('cartoChoisirFiltre');''',
    )

    # 4) JS : ecouteur de changement du select au lieu des clics sur chips
    remplacer(
        '''    chipsFiltre.forEach(function (chip) {
        chip.addEventListener('click', function () {
            aucunFiltreChoisi = false;
            themeActif = chip.getAttribute('data-theme-filtre') || '';
            chipsFiltre.forEach(function (c) { c.classList.toggle('active', c === chip); });
            appliquerRecherche();
        });
    });''',
        '''    if (selectFiltre) {
        selectFiltre.addEventListener('change', function () {
            aucunFiltreChoisi = false;
            const valeur = selectFiltre.value;
            themeActif = (valeur === '__TOUTES__') ? '' : valeur;
            appliquerRecherche();
        });
    }''',
    )

    if erreurs:
        print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
        for e in erreurs:
            print(" -", e)
    else:
        with open(CHEMIN, "w", encoding="utf-8") as f:
            f.write(contenu)
        print(f"OK : {remplacements_ok} modification(s) appliquee(s).")