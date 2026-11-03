# -*- coding: utf-8 -*-
"""
python audit_simulateur_10_diff2.py

Reprend la comparaison caractere par caractere avec l'ancre corrigee
(1px dashedvar), et continue APRES la premiere divergence trouvee pour
voir s'il y en a d'autres plus loin.
"""
import io

chemin = "foncier/templates/foncier/fiscalite.html"

ancre = """    if (data.depasse_seuil_cgu) {
      html += '<div class="warn-band" style="margin-top:16px;"><i class="fa-solid fa-triangle-exclamation"></i>' +
              '<p>Votre chiffre d\\'affaires dépasse le seuil de ' + fmtFCFA(data.seuil_cgu) + ' autorisé pour la CGU. Vous relevez probablement du régime réel (IS/TVA).</p></div>';
    }
  }

  html += '<p style="font-size:12px;color:var(--text-muted);margin-top:20px;padding-top:16px;border-top:1px dashedvar(--border);">' + data.reference + '</p>';"""

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

n = contenu.count(ancre)
print(f"Occurrences exactes de l'ancre : {n}\n")

if n == 1:
    print("OK - l'ancre correspond.")
else:
    idx = contenu.find("data.depasse_seuil_cgu) {")
    if idx == -1:
        print("Je ne retrouve meme pas 'data.depasse_seuil_cgu) {' dans le fichier.")
    else:
        debut = contenu.rfind("\n", 0, idx) + 1
        extrait_reel = contenu[debut: debut + len(ancre) + 10]

        print("=== Texte REEL (repr complet) ===")
        print(repr(extrait_reel))
        print()
        print("=== Mon ancre (repr complet) ===")
        print(repr(ancre))
        print()

        m = min(len(extrait_reel), len(ancre))
        divergences = []
        for i in range(m):
            if extrait_reel[i] != ancre[i]:
                divergences.append(i)

        if not divergences:
            if len(extrait_reel) != len(ancre):
                print(f"Identiques sur les {m} premiers caracteres, mais longueur differente "
                      f"(reel={len(extrait_reel)}, ancre={len(ancre)}).")
            else:
                print("Aucune divergence (etrange, le count() devrait trouver 1).")
        else:
            print(f"{len(divergences)} divergence(s) trouvee(s) :\n")
            for d in divergences[:10]:
                deb = max(0, d - 25)
                print(f"-- position {d} --")
                print(f"  REEL  : ...{extrait_reel[deb:d]!r} >>> {extrait_reel[d:d+15]!r}")
                print(f"  ANCRE : ...{ancre[deb:d]!r} >>> {ancre[d:d+15]!r}")
                print()