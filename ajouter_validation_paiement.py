CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancien_liste = '''    lignes = [
        {
            "pk": p.pk,
            "cellules": [
                format_html(
                    '<a href="{}" style="color:var(--green);font-weight:700;text-decoration:none;">'
                    '<i class="fa-solid fa-file-pdf"></i> {}</a>',
                    reverse("paiement_recu_pdf", args=[p.pk]), p.numero_recu,
                ),
                getattr(p.taxation, "contribuable", "—"),
                _fcfa(p.montant),
                p.date_paiement,
                p.get_mode_paiement_display(),
            ]
        }
        for p in paiements
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "paiements",
        "titre": "Paiements",
        "colonnes": ["N° reçu", "Contribuable", "Montant", "Date", "Mode"],'''

nouveau_liste = '''    def _cellule_statut(p):
        if p.statut_paiement == "CONFIRME":
            return format_html('<span class="badge" style="background:rgba(47,122,79,0.10); color:#2f7a4f;">Confirmé</span>')
        elif p.statut_paiement == "EN_ATTENTE":
            return format_html(
                '<span class="badge" style="background:rgba(185,116,11,0.10); color:#b9740b;">En attente</span> '
                '<a href="{}" style="margin-left:8px; color:var(--green); font-weight:700; font-size:12px; text-decoration:none;">'
                '<i class="fa-solid fa-check"></i> Valider</a>',
                reverse("dashboard_paiement_valider", args=[p.pk]),
            )
        else:
            return format_html('<span class="badge badge-danger">Échoué</span>')

    lignes = [
        {
            "pk": p.pk,
            "cellules": [
                format_html(
                    '<a href="{}" style="color:var(--green);font-weight:700;text-decoration:none;">'
                    '<i class="fa-solid fa-file-pdf"></i> {}</a>',
                    reverse("paiement_recu_pdf", args=[p.pk]), p.numero_recu,
                ),
                getattr(p.taxation, "contribuable", "—"),
                _fcfa(p.montant),
                p.date_paiement,
                p.get_mode_paiement_display(),
                _cellule_statut(p),
            ]
        }
        for p in paiements
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "paiements",
        "titre": "Paiements",
        "colonnes": ["N° reçu", "Contribuable", "Montant", "Date", "Mode", "Statut"],'''

if "_cellule_statut" in contenu:
    print("DEJA FAIT : liste deja modifiee.")
elif ancien_liste in contenu:
    contenu = contenu.replace(ancien_liste, nouveau_liste, 1)
    changements += 1
    print("OK : colonne Statut + bouton Valider ajoutes a la liste.")
else:
    print("ERREUR : bloc de la liste introuvable.")

AJOUT = '''

@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_paiement_valider(request, pk):
    """Valide un paiement encore 'En attente' (typiquement issu du
    backend de demonstration 'manuel') : le passe a 'Confirme', ce qui
    rend alors son recu PDF telechargeable par le citoyen."""
    paiement = get_object_or_404(Paiement, pk=pk)

    if paiement.statut_paiement == "EN_ATTENTE":
        paiement.statut_paiement = "CONFIRME"
        paiement.save(update_fields=["statut_paiement"])
        messages.success(request, f"Paiement {paiement.numero_recu} validé — le reçu est maintenant disponible.")
    else:
        messages.info(request, "Ce paiement n'était pas en attente de validation.")

    return redirect("dashboard_paiement_list")
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_paiement_valider" in contenu_a_jour:
    print("DEJA FAIT : vue de validation deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : vue dashboard_paiement_valider ajoutee.")

print(f"\n=== {changements} changement(s) enregistres. ===")