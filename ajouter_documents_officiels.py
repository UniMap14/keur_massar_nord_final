CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    Actualite,\n)"
nouveau_modele = "    Actualite,\n    ProfilCitoyen,\n)"

if "ProfilCitoyen," in contenu.split("from .models import (")[1].split(")")[0]:
    print("DEJA FAIT : ProfilCitoyen deja importe.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : ProfilCitoyen ajoute a l'import des modeles.")
else:
    print("ERREUR : ancre 'Actualite,\\n)' introuvable.")

AJOUT = '''

# ============================================================
# DOCUMENTS OFFICIELS (quitus fiscal, attestation de non-imposition) —
# meme style visuel que le recu de paiement (recu_pdf_view), genere en
# PDF avec reportlab. Principe SenTax : ces documents ne sont delivres
# que si la situation fiscale du contribuable le permet reellement.
# ============================================================

def _preparer_pdf_document(titre_document, numero_reference):
    """Cree le canvas ReportLab et dessine l'en-tete commun (bande verte,
    logo texte, titre du document). Renvoie (buffer, canvas, largeur,
    hauteur, marge, y_depart, couleurs)."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.colors import HexColor

    VERT_FONCE = HexColor("#3c2a20")
    OR = HexColor("#c9982e")
    GRIS = HexColor("#6b5d4f")
    BORDURE = HexColor("#e6e0d4")

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4
    marge = 20 * mm

    c.setFillColor(VERT_FONCE)
    c.rect(0, hauteur - 32 * mm, largeur, 32 * mm, fill=True, stroke=False)
    c.setFillColor(OR)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(marge, hauteur - 16 * mm, "KEUR MASSAR NORD")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 10)
    c.drawString(marge, hauteur - 23 * mm, "Commune de Keur Massar Nord — Foncier & Fiscal")

    c.setFillColor(OR)
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(largeur - marge, hauteur - 16 * mm, titre_document)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 10)
    c.drawRightString(largeur - marge, hauteur - 23 * mm, numero_reference)

    return buffer, c, largeur, hauteur, marge, hauteur - 46 * mm, (VERT_FONCE, OR, GRIS, BORDURE)


def _pied_de_page_document(c, marge, hauteur_page_url, texte_verif):
    """Pied de page commun (authenticite + date d'edition)."""
    from django.utils import timezone
    c.setFillColor(HexColor("#6b5d4f"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(marge, 18 * 2.834645669, texte_verif)
    c.drawString(marge, 13 * 2.834645669, f"Édité le {timezone.now().strftime('%d/%m/%Y')} depuis l'espace citoyen KEUR MASSAR NORD.")


@login_required
def quitus_fiscal_pdf_view(request):
    """
    Genere un QUITUS FISCAL en PDF : atteste que le contribuable est a
    jour de ses obligations fiscales communales. Refuse de le delivrer
    si ce n'est reellement pas le cas (document a valeur officielle).
    """
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    contribuable = profil.contribuable
    if contribuable.statut_global != "A_JOUR":
        messages.error(
            request,
            "Un quitus fiscal ne peut être délivré que si votre compte est à jour de tous vos paiements. "
            "Réglez vos taxations en retard puis réessayez."
        )
        return redirect("citoyen_espace")

    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor

    numero_doc = f"QF-{contribuable.numero_fiscal}-{timezone_now_str()}"
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "QUITUS FISCAL", numero_doc
    )

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "CONTRIBUABLE")
    y -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge, y, f"{contribuable.nom} {contribuable.prenom}")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"Identifiant fiscalité : {contribuable.numero_fiscal}")

    y -= 14 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 12 * mm

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 11)
    texte = (
        f"La commune de Keur Massar Nord atteste par le présent document que "
        f"{contribuable.nom} {contribuable.prenom} est, à la date d'édition, "
        f"À JOUR de l'ensemble de ses obligations fiscales communales "
        f"(taxes foncières sur les propriétés bâties et non bâties)."
    )
    from textwrap import wrap
    for ligne in wrap(texte, width=78):
        c.drawString(marge, y, ligne)
        y -= 6 * mm

    y -= 8 * mm
    c.setFillColor(OR)
    c.rect(marge, y - 4 * mm, largeur - 2 * marge, 18 * mm, fill=True, stroke=False)
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(marge + 6 * mm, y + 6 * mm, "TOTAL RÉGLÉ")
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(
        largeur - marge - 6 * mm, y + 5 * mm,
        f"{contribuable.montant_paye_total:,.0f} FCFA".replace(",", " ")
    )

    _pied_de_page_document(
        c, marge, hauteur,
        "Document généré électroniquement, à valeur informative. Son authenticité peut être "
        "vérifiée auprès des services fiscaux de la commune."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="quitus_fiscal_{contribuable.numero_fiscal}.pdf"'
    return response


@login_required
def attestation_non_imposition_pdf_view(request):
    """
    Genere une ATTESTATION DE NON-IMPOSITION en PDF : atteste que le
    contribuable n'est redevable d'aucune taxe communale. Refuse de la
    delivrer si le contribuable a bien des taxes dues (meme partiellement
    payees) — ce document a une signification precise, differente d'un
    simple "compte a jour".
    """
    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    contribuable = profil.contribuable
    if contribuable.montant_du_total and contribuable.montant_du_total > 0:
        messages.error(
            request,
            "Une attestation de non-imposition ne peut être délivrée qu'aux contribuables "
            "n'ayant aucune taxe communale à leur nom. Votre dossier comporte des taxations : "
            "un quitus fiscal peut être demandé une fois vos paiements à jour."
        )
        return redirect("citoyen_espace")

    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from textwrap import wrap

    numero_doc = f"ANI-{contribuable.numero_fiscal}-{timezone_now_str()}"
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "ATTESTATION DE NON-IMPOSITION", numero_doc
    )

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "CONTRIBUABLE")
    y -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge, y, f"{contribuable.nom} {contribuable.prenom}")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"Identifiant fiscalité : {contribuable.numero_fiscal}")

    y -= 14 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 12 * mm

    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica", 11)
    texte = (
        f"La commune de Keur Massar Nord atteste par le présent document que "
        f"{contribuable.nom} {contribuable.prenom} n'est, à la date d'édition, "
        f"redevable d'AUCUNE taxe foncière communale (CFPB/CFPNB) sur le territoire "
        f"de la commune."
    )
    for ligne in wrap(texte, width=78):
        c.drawString(marge, y, ligne)
        y -= 6 * mm

    _pied_de_page_document(
        c, marge, hauteur,
        "Document généré électroniquement, à valeur informative. Son authenticité peut être "
        "vérifiée auprès des services fiscaux de la commune."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="attestation_non_imposition_{contribuable.numero_fiscal}.pdf"'
    return response


def timezone_now_str():
    from django.utils import timezone
    return timezone.now().strftime("%Y%m%d")
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def quitus_fiscal_pdf_view" in contenu_a_jour:
    print("DEJA FAIT : vues documents officiels deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : 2 vues (quitus fiscal + attestation non-imposition) ajoutees.")

print(f"\n=== {changements} changement(s) enregistres. ===")