CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

changements = 0

ancre_modele = "    Signalement,\n)"
nouveau_modele = "    Signalement,\n    DeclarationFiscale,\n)"

if "DeclarationFiscale," in contenu and "from .models import" in contenu:
    print("DEJA FAIT : import DeclarationFiscale deja present.")
elif ancre_modele in contenu:
    contenu = contenu.replace(ancre_modele, nouveau_modele, 1)
    changements += 1
    print("OK : DeclarationFiscale ajoute a l'import des modeles.")
else:
    print("ERREUR : ancre 'Signalement,\\n)' introuvable.")

ancre_settings = "from django.conf import settings"
nouveau_settings = "from django.conf import settings\nfrom django.utils import timezone"

if "from django.utils import timezone" in contenu:
    print("DEJA FAIT : import timezone deja present.")
elif ancre_settings in contenu:
    contenu = contenu.replace(ancre_settings, nouveau_settings, 1)
    changements += 1
    print("OK : import timezone ajoute.")
else:
    print("ERREUR : ancre 'from django.conf import settings' introuvable.")

AJOUT = '''

# ============================================================
# DECLARATIONS FISCALES (cote agent) — examen et validation des
# declarations deposees par les citoyens (voir citoyens/views.py pour
# le depot cote citoyen). Reprend le meme bareme que
# simuler_fiscalite_fonciere.py, pour rester coherent avec les
# montants deja simules sur les parcelles.
# ============================================================

from decimal import Decimal, ROUND_HALF_UP

_TAUX_CFPB = Decimal("0.05")
_TAUX_CFPNB = Decimal("0.05")
_TAUX_SURTAXE_NON_BATI = Decimal("0.02")
_ABATTEMENT_RESIDENCE_PRINCIPALE = Decimal("1500000")

_VALEUR_M2_DECLARATION = {
    "Bâti": Decimal("14000"),
    "Terrain Nu": Decimal("100000"),
    "Zone de culture": Decimal("35000"),
}


def _calculer_montant_declaration(occupation, superficie):
    """Meme methode que simuler_fiscalite_fonciere.py (CFPB 5% avec
    abattement RP pour le bati, CFPNB 5%+2% de surtaxe pour le terrain
    nu, 5% sans surtaxe pour une zone de culture)."""
    superficie = Decimal(str(superficie or 0))
    if occupation == "Bâti":
        valeur_locative = superficie * _VALEUR_M2_DECLARATION["Bâti"]
        base = max(Decimal("0"), valeur_locative - _ABATTEMENT_RESIDENCE_PRINCIPALE)
        montant = base * _TAUX_CFPB
    else:
        valeur_venale = superficie * _VALEUR_M2_DECLARATION.get(occupation, Decimal("0"))
        taux = _TAUX_CFPNB + (_TAUX_SURTAXE_NON_BATI if occupation == "Terrain Nu" else Decimal("0"))
        montant = valeur_venale * taux
    return montant.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_declaration_list(request):
    """Liste des declarations fiscales, filtrable par statut (par
    defaut : celles encore a traiter)."""
    statut_filtre = request.GET.get("statut", "")
    qs = (
        DeclarationFiscale.objects
        .select_related("contribuable", "parcelle", "type_taxe")
        .order_by("-date_declaration")
    )
    if statut_filtre:
        qs = qs.filter(statut=statut_filtre)

    return render(request, "dashboard/declaration_list.html", {
        "active_section": "declarations",
        "declarations": qs,
        "statut_filtre": statut_filtre,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('fiscal')
def dashboard_declaration_traiter(request, pk):
    """Examen d'une declaration : validation (calcule et emet la
    taxation correspondante) ou rejet (avec motif)."""
    declaration = get_object_or_404(
        DeclarationFiscale.objects.select_related("contribuable", "parcelle", "type_taxe"),
        pk=pk,
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "valider":
            superficie = declaration.superficie_declaree or declaration.parcelle.superficie
            montant = _calculer_montant_declaration(declaration.occupation_declaree, superficie)

            taxation = Taxation.objects.create(
                contribuable=declaration.contribuable,
                type_taxe=declaration.type_taxe,
                parcelle=declaration.parcelle,
                annee_fiscale=declaration.annee_fiscale,
                montant_du=montant,
            )

            declaration.statut = DeclarationFiscale.STATUT_VALIDEE
            declaration.taxation_generee = taxation
            declaration.traite_par = request.user
            declaration.date_traitement = timezone.now()
            declaration.commentaire_agent = request.POST.get("commentaire_agent", "").strip()
            declaration.save()

            messages.success(request, f"Déclaration validée — taxation de {montant:,.0f} FCFA émise.".replace(",", " "))
            return redirect("dashboard_declaration_list")

        elif action == "rejeter":
            motif = request.POST.get("motif_rejet", "").strip()
            if not motif:
                messages.error(request, "Merci d'indiquer un motif de rejet.")
            else:
                declaration.statut = DeclarationFiscale.STATUT_REJETEE
                declaration.motif_rejet = motif
                declaration.traite_par = request.user
                declaration.date_traitement = timezone.now()
                declaration.save()
                messages.info(request, "Déclaration rejetée.")
                return redirect("dashboard_declaration_list")

    return render(request, "dashboard/declaration_traiter.html", {
        "active_section": "declarations",
        "declaration": declaration,
    })
'''

with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
    f.write(contenu)

with open(CHEMIN, encoding="utf-8") as f:
    contenu_a_jour = f.read()

if "def dashboard_declaration_list" in contenu_a_jour:
    print("DEJA FAIT : vues agent deja presentes.")
else:
    with open(CHEMIN, "a", encoding="utf-8", newline="") as f:
        f.write(AJOUT)
    changements += 1
    print("OK : fonction de calcul + 2 vues agent ajoutees a la fin du fichier.")

print(f"\n=== {changements} changement(s) enregistres. ===")