CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

@login_required
def extrait_cadastral_pdf_view(request, pk):
    """
    Genere l'extrait cadastral officiel en PDF pour une demande de
    service PRETE et payee (si payante). Reprend le meme style visuel
    que les autres documents (quitus, attestation, releve de compte).
    """
    from reportlab.lib.units import mm
    from .models import DemandeService

    demande = get_object_or_404(DemandeService, pk=pk, demandeur=request.user)

    if demande.statut != "PRETE":
        messages.error(request, "Ce document n'est pas encore prêt.")
        return redirect("citoyen_demande_detail", pk=pk)

    if demande.type_demande.tarif and demande.type_demande.tarif > 0 and demande.statut_paiement != "CONFIRME":
        messages.error(
            request,
            "Le paiement de cette démarche doit d'abord être validé avant de pouvoir télécharger le document."
        )
        return redirect("citoyen_demande_detail", pk=pk)

    parcelle = demande.parcelle
    if parcelle is None:
        messages.error(request, "Aucune parcelle n'est associée à cette démarche.")
        return redirect("citoyen_demande_detail", pk=pk)

    numero_doc = f"EC-{demande.numero_dossier}"
    buffer, c, largeur, hauteur, marge, y, (VERT_FONCE, OR, GRIS, BORDURE) = _preparer_pdf_document(
        "EXTRAIT CADASTRAL", numero_doc
    )

    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(marge, y, "PARCELLE")
    y -= 6 * mm
    c.setFillColor(VERT_FONCE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, parcelle.nicad)

    y -= 14 * mm
    c.setStrokeColor(BORDURE)
    c.line(marge, y, largeur - marge, y)
    y -= 10 * mm

    lignes = [
        ("Section cadastrale", parcelle.section_cadastrale or "—"),
        ("Numéro de parcelle", parcelle.numero_parcelle or "—"),
        ("Numéro de lot", parcelle.numero_lot or "—"),
        ("Numéro de titre foncier", parcelle.numero_titre_foncier or "—"),
        ("Superficie", f"{parcelle.superficie:,.0f} m²".replace(",", " ") if parcelle.superficie else "—"),
        ("Occupation du sol", parcelle.occupation_sol or "—"),
        ("Adresse / secteur", parcelle.adresse_parcelle or "—"),
        ("Zone", parcelle.zone.nom if parcelle.zone_id else "—"),
        ("Type de document", parcelle.get_type_document_display() if parcelle.type_document else "—"),
        ("Propriétaire", str(parcelle.proprietaire) if parcelle.proprietaire_id else "—"),
    ]
    for label, valeur in lignes:
        c.setFillColor(GRIS)
        c.setFont("Helvetica", 10)
        c.drawString(marge, y, label)
        c.setFillColor(VERT_FONCE)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(largeur - marge, y, str(valeur))
        y -= 8 * mm

    _pied_de_page_document(
        c, marge, hauteur,
        "Extrait cadastral délivré à titre informatif. Son authenticité peut être "
        "vérifiée auprès des services du cadastre de la commune."
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="extrait_cadastral_{parcelle.nicad}.pdf"'
    return response
'''

if "def extrait_cadastral_pdf_view" in contenu:
    print("DEJA FAIT : vue deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : vue extrait_cadastral_pdf_view ajoutee.")