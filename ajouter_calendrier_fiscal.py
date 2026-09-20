CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

AJOUT = '''

@login_required
def calendrier_fiscal_view(request):
    """
    Calendrier des echeances fiscales du citoyen connecte. Reprend
    exactement la meme logique de calcul de date que la commande
    envoyer_rappels_echeances (foncier/management/commands/), pour que
    l'affichage reste toujours coherent avec les rappels reellement
    envoyes par SMS/email.
    """
    import datetime
    from foncier.models import Taxation

    citoyen = getattr(request.user, "citoyen", None)
    if citoyen is None:
        messages.info(request, "Cette page est réservée aux citoyens inscrits.")
        return redirect("citoyen_login")

    profil = ProfilCitoyen.objects.filter(user=request.user, actif=True).select_related("contribuable").first()
    echeances = []

    if profil:
        taxations = (
            Taxation.objects.filter(contribuable=profil.contribuable)
            .select_related("type_taxe", "parcelle")
            .exclude(type_taxe__mois_echeance__isnull=True)
            .exclude(type_taxe__jour_echeance__isnull=True)
        )
        aujourdhui = datetime.date.today()

        for t in taxations:
            try:
                date_echeance = datetime.date(
                    aujourdhui.year, t.type_taxe.mois_echeance, t.type_taxe.jour_echeance
                )
            except ValueError:
                continue

            jours_restants = (date_echeance - aujourdhui).days

            if t.solde <= 0:
                statut_calendrier = "payee"
            elif jours_restants < 0:
                statut_calendrier = "en_retard"
            elif jours_restants <= 30:
                statut_calendrier = "proche"
            else:
                statut_calendrier = "a_venir"

            echeances.append({
                "taxation": t,
                "date_echeance": date_echeance,
                "jours_restants": jours_restants,
                "statut_calendrier": statut_calendrier,
            })

        echeances.sort(key=lambda e: e["date_echeance"])

    return render(request, "citoyens/espace/calendrier_fiscal.html", {
        "echeances": echeances,
        "citoyen": citoyen,
        "active_section": "calendrier",
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def calendrier_fiscal_view" in contenu_a_jour:
    print("DEJA FAIT : vue deja presente.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    print("OK : vue calendrier_fiscal_view ajoutee a la fin du fichier.")