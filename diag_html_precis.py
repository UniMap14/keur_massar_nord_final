# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail_admin.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

ancien_html = '''          <div id="selOccupation" class="geo-tool-result" style="color:#766c5d;"></div>
          <div id="selection-liste" class="geo-selection-liste"></div>
          <div style="display:flex; gap:8px; margin-top:10px;">
            <button type="button" id="btnSelectionCSV" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-file-csv"></i> CSV</button>
            <button type="button" id="btnSelectionGeoJSON" class="geo-btn geo-btn-ghost geo-btn-block"><i class="fa-solid fa-map"></i> GeoJSON</button>
          </div>
          <button type="button" id="btnSelectionEffacer" class="geo-btn geo-btn-ghost geo-btn-block"style="margin-top:8px;"><i class="fa-solid fa-trash"></i> Effacer la sélection</button>'''

idx = contenu.find('<div id="selOccupation"')
if idx == -1:
    print("Motif de base introuvable du tout !")
else:
    debut = contenu.rfind("\n", 0, idx) + 1
    segment_reel = contenu[debut:debut+len(ancien_html)]
    if segment_reel == ancien_html:
        print("IDENTIQUE - bizarre, ca devrait marcher.")
    else:
        print("DIFFERENCE TROUVEE.")
        for i, (a, b) in enumerate(zip(ancien_html, segment_reel)):
            if a != b:
                print(f"Position {i}: attendu {repr(a)} ({ord(a)}) vs reel {repr(b)} ({ord(b)})")
                print("Contexte attendu:", repr(ancien_html[max(0,i-40):i+40]))
                print("Contexte reel   :", repr(segment_reel[max(0,i-40):i+40]))
                break
        else:
            print("Meme contenu jusqu'a la longueur min, mais longueurs differentes:")
            print("longueur attendue:", len(ancien_html), "longueur reelle:", len(segment_reel))