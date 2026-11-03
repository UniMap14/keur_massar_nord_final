# -*- coding: utf-8 -*-
"""
python audit_simulateur_9_diff.py

Compare caractere par caractere mon ancre avec le texte reel du
fichier, et affiche precisement ou ca diverge (au lieu de deviner).
"""
import io

chemin = "foncier/templates/foncier/fiscalite.html"

ancre = """    if (data.depasse_seuil_cgu) {
      html += '<div class="warn-band" style="margin-top:16px;"><i class="fa-solid fa-triangle-exclamation"></i>' +
              '<p>Votre chiffre d\\'affaires dépasse le seuil de ' + fmtFCFA(data.seuil_cgu) + ' autorisé pour la CGU. Vous relevez probablement du régime réel (IS/TVA).</p></div>';
    }
  }

  html += '<p style="font-size:12px;color:var(--text-muted);margin-top:20px;padding-top:16px;border-top:1pxdashed var(--border);">' + data.reference + '</p>';"""

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

n = contenu.count(ancre)
print(f"Occurrences exactes de l'ancre : {n}\n")

if n == 1:
    print("OK - l'ancre correspond maintenant (bizarre que le script precedent ait echoue).")
else:
    # Recherche approximative : on localise "depasse_seuil_cgu" dans le fichier
    # et on affiche le texte reel autour, ligne par ligne avec repr(),
    # puis on compare caractere par caractere avec l'ancre.
    idx = contenu.find("data.depasse_seuil_cgu) {")
    if idx == -1:
        print("Je ne retrouve meme pas 'data.depasse_seuil_cgu) {' dans le fichier.")
    else:
        debut = contenu.rfind("\n", 0, idx) + 1
        extrait_reel = contenu[debut: debut + len(ancre) + 40]
        print("=== Texte REEL du fichier a cet endroit (repr) ===")
        print(repr(extrait_reel))
        print()
        print("=== Mon ancre (repr) ===")
        print(repr(ancre))
        print()
        # comparaison caractere par caractere
        m = min(len(extrait_reel), len(ancre))
        divergence = None
        for i in range(m):
            if extrait_reel[i] != ancre[i]:
                divergence = i
                break
        if divergence is None:
            if len(extrait_reel) != len(ancre):
                print(f"Les deux textes sont identiques sur les {m} premiers caracteres, "
                      f"mais la longueur differe (reel={len(extrait_reel)}, ancre={len(ancre)}).")
            else:
                print("Aucune divergence trouvee (etrange).")
        else:
            debut_ctx = max(0, divergence - 30)
            print(f"Premiere divergence au caractere {divergence} :")
            print(f"  REEL  : ...{extrait_reel[debut_ctx:divergence]}[{extrait_reel[divergence:divergence+20]!r}]...")
            print(f"  ANCRE : ...{ancre[debut_ctx:divergence]}[{ancre[divergence:divergence+20]!r}]...")