# -*- coding: utf-8 -*-
"""
Ajoute, pour le Chef/Gestionnaire Cadastre, une carte KPI "Montant encaisse
(demarches cadastre)" sur le tableau de bord, calculee a partir des
montants payes par les citoyens pour leurs demarches en ligne (ex :
extrait cadastral), hors fiscalite.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_montant_cadastre.py
"""
import os

CHEMIN_VIEWS = os.path.join("foncier", "dashboard_views.py")
CHEMIN_HTML = os.path.join("foncier", "templates", "dashboard", "home.html")

# ------------------------------------------------------------------
# 1) dashboard_views.py : calculer le montant encaisse via DemandeService
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_VIEWS):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_VIEWS}")

with open(CHEMIN_VIEWS, "r", encoding="utf-8") as f:
    contenu_views = f.read()

ANCRE_CALCUL = (
    '    total_recouvre = Paiement.objects.aggregate(Sum("montant"))["montant__sum"] or 0\n'
    '    total_du = Taxation.objects.aggregate(Sum("montant_du"))["montant_du__sum"] or 0\n'
    '    parcelles_en_retard = Parcelle.objects.filter(statut_fiscal="EN_RETARD").count()'
)
REMPLACEMENT_CALCUL = (
    '    total_recouvre = Paiement.objects.aggregate(Sum("montant"))["montant__sum"] or 0\n'
    '    total_du = Taxation.objects.aggregate(Sum("montant_du"))["montant_du__sum"] or 0\n'
    '    parcelles_en_retard = Parcelle.objects.filter(statut_fiscal="EN_RETARD").count()\n'
    '\n'
    '    # Montant encaisse via les demarches en ligne (ex : extrait cadastral),\n'
    '    # hors fiscalite -- ce que le Chef/Gestionnaire Cadastre doit voir.\n'
    '    total_recouvre_demandes = DemandeService.objects.exclude(\n'
    '        type_demande__categorie="FISCALITE"\n'
    '    ).filter(\n'
    '        statut_paiement=DemandeService.STATUT_PAIEMENT_CONFIRME\n'
    '    ).aggregate(t=Sum("montant_paye"))["t"] or 0'
)

ANCRE_CONTEXTE = '        "total_proprios": total_proprios,\n'
REMPLACEMENT_CONTEXTE = (
    '        "total_proprios": total_proprios,\n'
    '        "total_recouvre_demandes_fmt": _fcfa(total_recouvre_demandes),\n'
)

deja_ok_views = "total_recouvre_demandes" in contenu_views

if not deja_ok_views:
    for ancre, nom in [(ANCRE_CALCUL, "CALCUL"), (ANCRE_CONTEXTE, "CONTEXTE")]:
        if ancre not in contenu_views:
            raise SystemExit(
                f"ERREUR : ancre {nom} introuvable dans dashboard_views.py.\n"
                "Le fichier a peut-etre deja ete modifie. Aucun changement effectue."
            )
        if contenu_views.count(ancre) != 1:
            raise SystemExit(f"ERREUR : ancre {nom} trouvee plusieurs fois, patch annule par securite.")
    contenu_views = contenu_views.replace(ANCRE_CALCUL, REMPLACEMENT_CALCUL)
    contenu_views = contenu_views.replace(ANCRE_CONTEXTE, REMPLACEMENT_CONTEXTE)
    with open(CHEMIN_VIEWS, "w", encoding="utf-8") as f:
        f.write(contenu_views)

# ------------------------------------------------------------------
# 2) home.html : afficher la nouvelle carte KPI pour le Cadastre
# ------------------------------------------------------------------
if not os.path.exists(CHEMIN_HTML):
    raise SystemExit(f"ERREUR : fichier introuvable : {CHEMIN_HTML}")

with open(CHEMIN_HTML, "r", encoding="utf-8") as f:
    contenu_html = f.read()

ANCRE_HTML = (
    '  <div class="kpi-card tone-blue">\n'
    '    <div class="kpi-icon"><i class="fa-solid fa-users"></i></div>\n'
    '    <span class="kpi-corner-icon"><i class="fa-solid fa-users"></i></span>\n'
    '    <div class="label">Propriétaires enregistrés</div>\n'
    '    <div class="value">{{ total_proprios }}</div>\n'
    '    <div class="delta">Citoyens dans la base SIG</div>\n'
    '  </div>\n'
    '\n'
    '{% endif %}'
)
REMPLACEMENT_HTML = (
    '  <div class="kpi-card tone-blue">\n'
    '    <div class="kpi-icon"><i class="fa-solid fa-users"></i></div>\n'
    '    <span class="kpi-corner-icon"><i class="fa-solid fa-users"></i></span>\n'
    '    <div class="label">Propriétaires enregistrés</div>\n'
    '    <div class="value">{{ total_proprios }}</div>\n'
    '    <div class="delta">Citoyens dans la base SIG</div>\n'
    '  </div>\n'
    '\n'
    '  <div class="kpi-card tone-green">\n'
    '    <div class="kpi-icon"><i class="fa-solid fa-sack-dollar"></i></div>\n'
    '    <span class="kpi-corner-icon"><i class="fa-solid fa-sack-dollar"></i></span>\n'
    '    <div class="label">Montant encaissé (démarches)</div>\n'
    '    <div class="value">{{ total_recouvre_demandes_fmt }}</div>\n'
    '    <div class="delta">Extraits cadastraux et autres démarches payées</div>\n'
    '  </div>\n'
    '\n'
    '{% endif %}'
)

deja_ok_html = "total_recouvre_demandes_fmt" in contenu_html

if not deja_ok_html:
    if ANCRE_HTML not in contenu_html:
        raise SystemExit(
            "ERREUR : ancre HTML introuvable dans home.html.\n"
            "Le fichier a peut-etre deja ete modifie. Aucun changement effectue."
        )
    if contenu_html.count(ANCRE_HTML) != 1:
        raise SystemExit("ERREUR : ancre HTML trouvee plusieurs fois, patch annule par securite.")
    contenu_html = contenu_html.replace(ANCRE_HTML, REMPLACEMENT_HTML)
    with open(CHEMIN_HTML, "w", encoding="utf-8") as f:
        f.write(contenu_html)

if deja_ok_views and deja_ok_html:
    print("OK : deja applique, rien a faire.")
else:
    print("OK : nouvelle carte 'Montant encaisse (demarches)' ajoutee pour le Cadastre.")
    print("-> foncier/dashboard_views.py : calcul ajoute" + (" (deja a jour)" if deja_ok_views else ""))
    print("-> foncier/templates/dashboard/home.html : carte ajoutee" + (" (deja a jour)" if deja_ok_html else ""))
    print("-> Redemarrez le serveur Django puis rechargez /gestion/.")