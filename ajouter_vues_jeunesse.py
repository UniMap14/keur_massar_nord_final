CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''    return render(request, "dashboard/morcellement_fusion_traiter.html", {
        "active_section": "morcellement_fusion",
        "demande": demande,
    })'''

nouvelles_vues = '''

# ============================================================
# ESPACE JEUNES (cote agent) — examen des projets soumis par les
# jeunes de la commune (voir jeunesse/views.py pour le depot public).
# Aucune restriction de role : accessible a tout agent, comme les
# Demarches en ligne et les Messages de contact.
# ============================================================

@staff_member_required(login_url='dashboard_login')
def dashboard_jeunesse_list(request):
    from jeunesse.models import ProjetJeune

    statut_filtre = request.GET.get("statut", "").strip()
    secteur_filtre = request.GET.get("secteur", "").strip()

    projets = ProjetJeune.objects.order_by("-date_soumission")
    if statut_filtre:
        projets = projets.filter(statut=statut_filtre)
    if secteur_filtre:
        projets = projets.filter(secteur=secteur_filtre)

    lignes = [
        {
            "pk": p.pk,
            "cellules": [
                p.titre_projet,
                p.nom_porteur,
                p.get_secteur_display(),
                p.get_statut_display(),
                p.date_soumission.strftime("%d/%m/%Y"),
            ],
        }
        for p in projets
    ]

    return render(request, "dashboard/generic_list_stub.html", {
        "active_section": "jeunesse",
        "titre": "Projets Jeunes",
        "colonnes": ["Projet", "Porteur", "Secteur", "Statut", "Déposé le"],
        "objets": lignes,
        "update_url_name": "dashboard_jeunesse_detail",
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_jeunesse_detail(request, pk):
    from jeunesse.models import ProjetJeune, MessageProjet

    projet = get_object_or_404(ProjetJeune, pk=pk)

    if request.method == "POST":
        nouveau_statut = request.POST.get("statut", "").strip()
        if nouveau_statut in dict(ProjetJeune.STATUT_CHOICES):
            projet.statut = nouveau_statut
        projet.motif_rejet = request.POST.get("motif_rejet", "").strip()
        projet.contacte = request.POST.get("contacte") == "on"
        projet.traite_par = request.user
        projet.date_traitement = timezone.now()
        projet.save()

        message_texte = request.POST.get("message", "").strip()
        if message_texte:
            MessageProjet.objects.create(
                projet=projet, contenu=message_texte, envoye_par=request.user
            )
            if projet.email:
                try:
                    send_mail(
                        subject=f"[KEUR MASSAR NORD] Votre projet « {projet.titre_projet} »",
                        message=message_texte,
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=[projet.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

        messages.success(request, "Projet mis à jour.")
        return redirect("dashboard_jeunesse_list")

    return render(request, "dashboard/jeunesse_detail.html", {
        "active_section": "jeunesse",
        "projet": projet,
        "messages_projet": projet.messages.all(),
    })'''

if "dashboard_jeunesse_list" in contenu:
    print("IGNORE : vues Jeunesse deja presentes.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, ancre + nouvelles_vues, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : vues dashboard_jeunesse_list et dashboard_jeunesse_detail ajoutees.")
else:
    print("ERREUR : point d'ancrage introuvable (fin de fichier inattendue).")