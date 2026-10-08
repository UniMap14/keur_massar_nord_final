CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''    return render(request, "dashboard/jeunesse_detail.html", {
        "active_section": "jeunesse",
        "projet": projet,
        "messages_projet": projet.messages.all(),
    })'''

nouvelles_vues = '''


# ============================================================
# GALERIE PHOTO (cote agent) — gestion des photos affichees sur la
# page publique "La commune en images" (foncier/views.py:galerie).
# ============================================================

class PhotoGalerieForm(forms.ModelForm):
    class Meta:
        from .models import PhotoGalerie
        model = PhotoGalerie
        fields = ["titre", "photo", "ordre"]


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_galerie_list(request):
    from .models import PhotoGalerie
    photos = PhotoGalerie.objects.order_by("ordre", "-date_ajout")
    return render(request, "dashboard/galerie_list.html", {
        "active_section": "galerie",
        "photos": photos,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('gestionnaire_technique')
def dashboard_galerie_create(request):
    if request.method == "POST":
        form = PhotoGalerieForm(request.POST, request.FILES)
        if form.is_valid():
            photo_obj = form.save()
            messages.success(request, f"Photo « {photo_obj.titre} » ajoutée avec succès.")
            return redirect("dashboard_galerie_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = PhotoGalerieForm()

    return render(request, "dashboard/galerie_form.html", {
        "active_section": "galerie", "form": form, "mode": "create",
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_galerie_update(request, pk):
    from .models import PhotoGalerie
    photo_obj = get_object_or_404(PhotoGalerie, pk=pk)

    if request.method == "POST":
        form = PhotoGalerieForm(request.POST, request.FILES, instance=photo_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Photo « {photo_obj.titre} » mise à jour.")
            return redirect("dashboard_galerie_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = PhotoGalerieForm(instance=photo_obj)

    return render(request, "dashboard/galerie_form.html", {
        "active_section": "galerie", "form": form, "mode": "update", "photo_obj": photo_obj,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('chef_technique')
def dashboard_galerie_delete(request, pk):
    from .models import PhotoGalerie
    photo_obj = get_object_or_404(PhotoGalerie, pk=pk)

    if request.method == "POST":
        titre = photo_obj.titre
        photo_obj.delete()
        messages.success(request, f"Photo « {titre} » supprimée.")
        return redirect("dashboard_galerie_list")

    return render(request, "dashboard/generic_confirm_delete.html", {
        "active_section": "galerie",
        "titre": "Photo",
        "list_url_name": "dashboard_galerie_list",
        "objet_str": str(photo_obj),
    })'''

if "dashboard_galerie_list" in contenu:
    print("IGNORE : vues galerie deja presentes.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, ancre + nouvelles_vues, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : 4 vues galerie ajoutees.")
else:
    print("ERREUR : point d'ancrage introuvable.")