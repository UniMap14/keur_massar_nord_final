# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

chemin = "foncier/templates/foncier/geoportail.html"
with io.open(chemin, "r", encoding="utf-8") as f:
    lignes = f.readlines()

debut = 1653  # ligne 1654 (0-index 1653)
fin = 1673    # juste avant afficherResultatSelection (ligne 1673)
print("=== calculerSelection, lignes", debut+1, "-", fin, "===")
print("".join(lignes[debut:fin]))
print()

# panneau HTML complet de la section selection spatiale (lignes ~550-575)
print("=== Panneau HTML selection spatiale, lignes 545-575 ===")
print("".join(lignes[544:575]))