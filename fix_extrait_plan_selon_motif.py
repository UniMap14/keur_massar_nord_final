# -*- coding: utf-8 -*-
"""
Rend le titre (et la mention entre parentheses du Lot) de l'extrait de
plan dependant du motif reel de la demande (type_demande.libelle) :
- Autorisation de construire -> "PLAN POUR AUTORISATION DE CONSTRUIRE"
- Demande de regularisation  -> "PLAN POUR REGULARISATION" + reference
  de l'arrete entre parentheses (parcelle.reference_arrete), comme sur
  le vrai modele.
- Situation / Delimitation / Autres -> titre adapte, sans arrete.

Usage (depuis C:\\Users\\DELL\\Desktop\\projet_kmsn\\projet_kms\\kmsn) :
    python fix_extrait_plan_selon_motif.py
"""
import io

chemin = "foncier/views.py"

with io.open(chemin, "r", encoding="utf-8") as f:
    contenu = f.read()

marqueur = "TITRES_PAR_MOTIF"
if marqueur in contenu:
    print("Deja applique, rien a faire.")
    raise SystemExit()

ancre = '''    titre_foncier = parcelle.numero_titre_foncier or "-"
    parcelle_label = parcelle.numero_parcelle or parcelle.nicad
    zone_label = parcelle.zone.nom if parcelle.zone_id else ""

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(largeur / 2, y, "PLAN POUR AUTORISATION DE CONSTRUIRE")
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    if parcelle.numero_titre_foncier:
        c.drawCentredString(largeur / 2, y, "Mt du Titre Foncier {}/DP".format(titre_foncier))
        y -= 5 * mm
    libelle_lot = "Lot n° {}".format(parcelle_label)
    if zone_label:
        libelle_lot += " ({})".format(zone_label)
    c.drawCentredString(largeur / 2, y, libelle_lot)'''

remplacement = '''    titre_foncier = parcelle.numero_titre_foncier or "-"
    parcelle_label = parcelle.numero_parcelle or parcelle.nicad
    zone_label = parcelle.zone.nom if parcelle.zone_id else ""
    reference_arrete = (getattr(parcelle, "reference_arrete", "") or "").strip()

    TITRES_PAR_MOTIF = {
        "Extrait de plan — Autorisation de construire": "PLAN POUR AUTORISATION DE CONSTRUIRE",
        "Extrait de plan — Demande de régularisation": "PLAN POUR REGULARISATION",
        "Extrait de plan — Situation": "PLAN DE SITUATION",
        "Extrait de plan — Délimitation": "PLAN DE DELIMITATION",
        "Extrait de plan — Autres": "EXTRAIT DE PLAN",
    }
    motif_libelle = demande.type_demande.libelle if demande.type_demande_id else ""
    est_regularisation = motif_libelle == "Extrait de plan — Demande de régularisation"
    titre_document_plan = TITRES_PAR_MOTIF.get(motif_libelle, "EXTRAIT DE PLAN FONCIER")

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(largeur / 2, y, titre_document_plan)
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    if parcelle.numero_titre_foncier:
        c.drawCentredString(largeur / 2, y, "Mt du Titre Foncier {}/DP".format(titre_foncier))
        y -= 5 * mm
    libelle_lot = "Lot n° {}".format(parcelle_label)
    if est_regularisation and reference_arrete:
        libelle_lot += " (Arrêté n° {})".format(reference_arrete)
    elif zone_label:
        libelle_lot += " ({})".format(zone_label)
    c.drawCentredString(largeur / 2, y, libelle_lot)'''

if ancre not in contenu:
    raise SystemExit("ANCRE INTROUVABLE - abandon, rien n'a ete modifie.")
if contenu.count(ancre) != 1:
    raise SystemExit("ANCRE trouvee plusieurs fois - abandon par securite.")

contenu = contenu.replace(ancre, remplacement)

with io.open(chemin, "w", encoding="utf-8") as f:
    f.write(contenu)
print("OK : le titre et la mention du Lot s'adaptent maintenant au motif de la demande.")