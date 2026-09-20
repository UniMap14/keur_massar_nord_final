CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

@login_required
def releve_compte_pdf_view(request):
    """
    Genere un RELEVE DE COMPTE FISCAL en PDF : recapitulatif de TOUTES
    les taxations du contribuable, toutes annees confondues (pas
    seulement un recu de paiement unique). Reprend le meme style
    visuel que les autres documents (quitus, attestation).
    """
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from foncier.models import Taxation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    if profil is None:
        messages.error(request, "Votre compte n'est pas encore relié à un dossier fiscal.")
        return redirect("citoyen_espace")

    contribuable = profil.contribuable
    taxations = (
        Taxation.objects.filter(contribuable=contribuable)
        .select_related("type_taxe", "parcelle")
        .order_by("-annee_fiscale")
    )

    numero_doc = f"RC-{contribuable.numero_fiscal}-{timezone_now_str()}"
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "RELEVÉ DE COMPTE", numero_doc
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

    y -= 12 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 10 * mm

    # --- En-tete du tableau ---
    def dessiner_entete_tableau(y_pos):
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(marge, y_pos, "ANNÉE")
        c.drawString(marge + 22 * mm, y_pos, "TAXE")
        c.drawString(marge + 70 * mm, y_pos, "PARCELLE")
        c.drawRightString(marge + 122 * mm, y_pos, "DÛ")
        c.drawRightString(marge + 145 * mm, y_pos, "PAYÉ")
        c.drawRightString(largeur - marge, y_pos, "STATUT")
        y_pos -= 4 * mm
        c.setStrokeColor(BORDURE)
        c.line(marge, y_pos, largeur - marge, y_pos)
        return y_pos - 6 * mm

    y = dessiner_entete_tableau(y)

    total_du = Decimal("0")
    total_paye = Decimal("0")

    for t in taxations:
        if y < 30 * mm:
            # Page pleine : nouvelle page, redessine l'en-tete
            _pied_de_page_document(
                c, marge, hauteur,
                "Document généré électroniquement, à valeur informative."
            )
            c.showPage()
            c.setFillColor(VERT_FONCE)
            y = hauteur - 20 * mm
            y = dessiner_entete_tableau(y)

        statut_label = "À jour" if t.statut == "A_JOUR" else "En retard"
        parcelle_label = t.parcelle.nicad if t.parcelle_id else "—"

        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica", 8.5)
        c.drawString(marge, y, str(t.annee_fiscale))
        c.drawString(marge + 22 * mm, y, t.type_taxe.libelle[:28])
        c.drawString(marge + 70 * mm, y, parcelle_label[:20])
        c.drawRightString(marge + 122 * mm, y, f"{t.montant_du:,.0f}".replace(",", " "))
        c.drawRightString(marge + 145 * mm, y, f"{t.montant_paye:,.0f}".replace(",", " "))
        c.setFillColor(HexColor("#2f7a4f") if t.statut == "A_JOUR" else HexColor("#b23b2e"))
        c.drawRightString(largeur - marge, y, statut_label)

        total_du += t.montant_du
        total_paye += t.montant_paye
        y -= 7 * mm

    y -= 6 * mm
    c.setFillColor(OR)
    c.rect(marge, y - 4 * mm, largeur - 2 * marge, 18 * mm, fill=True, stroke=False)
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(marge + 6 * mm, y + 7 * mm, "TOTAL DÛ (toutes années)")
    c.drawString(marge + 6 * mm, y + 1 * mm, "TOTAL RÉGLÉ (toutes années)")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(largeur - marge - 6 * mm, y + 7 * mm, f"{total_du:,.0f} FCFA".replace(",", " "))
    c.drawRightString(largeur - marge - 6 * mm, y + 1 * mm, f"{total_paye:,.0f} FCFA".replace(",", " "))

    _pied_de_page_document(
        c, marge, hauteur,
        "Document généré électroniquement, à valeur informative. Son authenticité peut être "
        "vérifiée auprès des services fiscaux de la commune."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="releve_compte_{contribuable.numero_fiscal}.pdf"'
    return response
'''

if "def releve_compte_pdf_view" in contenu:
    print("DEJA FAIT : vue deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : vue releve_compte_pdf_view ajoutee.")