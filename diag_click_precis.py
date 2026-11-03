# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

ancien_click = '''    map.on('click', function (e) {
      if (modeChoixRayon) {
        modeChoixRayon = false;
        const conteneurCarteR = document.getElementById('map');
        if (conteneurCarteR) conteneurCarteR.style.cursor = '';
        const btnRayon = document.getElementById('btnRayonPointLibre');
        if (btnRayon) btnRayon.innerHTML = '<i class="fa-solid fa-map-pin"></i> Choisir un point sur la carte';
        const selectInfra = document.getElementById('rayon-infra-select');
        if (selectInfra) selectInfra.value = '';
        const rayon = parseInt(document.getElementById('rayon-slider').value, 10);
        calculerRayonAutour(e.latlng, rayon);
        return;
      }
      if (!modeMesure) return;
      pointsMesure.push(e.latlng);
      redessinerMesure();
    });

    const btnRayonPointLibre = document.getElementById('btnRayonPointLibre');
    if (btnRayonPointLibre) {
      btnRayonPointLibre.addEventListener('click', function () {
        modeChoixRayon = true;
        const conteneurCarte = document.getElementById('map');
        if (conteneurCarte) conteneurCarte.style.cursor = 'crosshair';
        btnRayonPointLibre.innerHTML = '<i class="fa-solid fa-crosshairs"></i> Clique sur la cartepour choisir...';
      });
    }'''

idx = contenu.find("map.on('click', function (e) {")
if idx == -1:
    print("Motif de base introuvable du tout !")
else:
    debut = contenu.rfind("\n", 0, idx) + 1
    segment_reel = contenu[debut:debut+len(ancien_click)]
    if segment_reel == ancien_click:
        print("IDENTIQUE - bizarre, ca devrait marcher.")
    else:
        print("DIFFERENCE TROUVEE.")
        for i, (a, b) in enumerate(zip(ancien_click, segment_reel)):
            if a != b:
                print(f"Position {i}: attendu {repr(a)} ({ord(a)}) vs reel {repr(b)} ({ord(b)})")
                print("Contexte attendu:", repr(ancien_click[max(0,i-30):i+30]))
                print("Contexte reel   :", repr(segment_reel[max(0,i-30):i+30]))
                break
        else:
            print("Meme contenu jusqu'a la longueur min, mais longueurs differentes:")
            print("longueur attendue:", len(ancien_click), "longueur reelle:", len(segment_reel))