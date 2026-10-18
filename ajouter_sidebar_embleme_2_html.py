# -*- coding: utf-8 -*-
"""
Insere le bloc HTML de l'embleme dore + tagline, juste avant le bloc
sidebar-footer (profil utilisateur / deconnexion), dans
dashboard/base.html.

Idempotent.
"""
CHEMIN = "foncier/templates/dashboard/base.html"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''    <div class="sidebar-footer">
      <div class="sidebar-user">'''

NOUVEAU = '''    <div class="sidebar-emblem">
      <div class="sidebar-emblem-icon"><i class="fa-solid fa-landmark-dome"></i></div>
      <p class="sidebar-emblem-tagline">Une commune connectee<br>pour un foncier securise</p>
    </div>

    <div class="sidebar-footer">
      <div class="sidebar-user">'''

if 'class="sidebar-emblem"' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (sidebar-footer / sidebar-user)")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")