CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancre = '''    return render(request, "dashboard/generic_confirm_delete.html", {
        "active_section": "galerie",
        "titre": "Photo",
        "list_url_name": "dashboard_galerie_list",
        "objet_str": str(photo_obj),
    })'''

nouvelles_vues = '''


# ============================================================
# CARTOTHEQUE (cote agent) — gestion des cartes thematiques affichees
# sur la page publique "Cartotheque" (foncier/views.py:cartotheque).
# ============================================================

class CarteThematiqueForm(forms.ModelForm):
    class Meta:
        from .models import CarteThematique
        model = CarteThematique
        fields = ["titre", "explication", "image", "ordre"]
        widgets = {
            "explication": forms.Textarea(attrs={"rows": 4}),
        }


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_cartotheque_list(request):
    from .models import CarteThematique
    cartes = CarteThematique.objects.order_by("ordre", "-date_ajout")
    return render(request, "dashboard/cartotheque_list.html", {
        "active_section": "cartotheque",
        "cartes": cartes,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('gestionnaire_technique')
def dashboard_cartotheque_create(request):
    if request.method == "POST":
        form = CarteThematiqueForm(request.POST, request.FILES)
        if form.is_valid():
            carte = form.save()
            messages.success(request, f"Carte « {carte.titre} » ajoutée avec succès.")
            return redirect("dashboard_cartotheque_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = CarteThematiqueForm()

    return render(request, "dashboard/cartotheque_form.html", {
        "active_section": "cartotheque", "form": form, "mode": "create",
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('technique')
def dashboard_cartotheque_update(request, pk):
    from .models import CarteThematique
    carte = get_object_or_404(CarteThematique, pk=pk)

    if request.method == "POST":
        form = CarteThematiqueForm(request.POST, request.FILES, instance=carte)
        if form.is_valid():
            form.save()
            messages.success(request, f"Carte « {carte.titre} » mise à jour.")
            return redirect("dashboard_cartotheque_list")
        messages.error(request, "Le formulaire contient des erreurs. Merci de vérifier les champs.")
    else:
        form = CarteThematiqueForm(instance=carte)

    return render(request, "dashboard/cartotheque_form.html", {
        "active_section": "cartotheque", "form": form, "mode": "update", "carte": carte,
    })


@staff_member_required(login_url='dashboard_login')
@role_requis('chef_technique')
def dashboard_cartotheque_delete(request, pk):
    from .models import CarteThematique
    carte = get_object_or_404(CarteThematique, pk=pk)

    if request.method == "POST":
        titre = carte.titre
        carte.delete()
        messages.success(request, f"Carte « {titre} » supprimée.")
        return redirect("dashboard_cartotheque_list")

    return render(request, "dashboard/generic_confirm_delete.html", {
        "active_section": "cartotheque",
        "titre": "Carte",
        "list_url_name": "dashboard_cartotheque_list",
        "objet_str": str(carte),
    })'''

if "dashboard_cartotheque_list" in contenu:
    print("IGNORE : vues cartotheque deja presentes.")
elif ancre in contenu:
    contenu = contenu.replace(ancre, ancre + nouvelles_vues, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : 4 vues cartotheque ajoutees.")
else:
    print("ERREUR : point d'ancrage introuvable.")