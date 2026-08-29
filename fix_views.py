import io

CHEMIN = "foncier/views.py"

with io.open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

ancien_import_1 = "from django.shortcuts import render, redirect\n"
nouveau_import_1 = "from django.shortcuts import render, redirect, get_object_or_404\n"

ancien_import_2 = "from django.core.exceptions import PermissionDenied\n"
nouveau_import_2 = "from django.core.exceptions import PermissionDenied, ValidationError\n"

ancienne_fonction = '''def signalement(request):
    if request.method == 'POST':
        form = SignalementForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre signalement a bien été enregistré. Merci pour votre contribution.")
            return redirect('signalement')
    else:
        form = SignalementForm()

    # Les signalements sont confidentiels : ils ne sont plus listés ici.
    # Ils sont visibles uniquement par l'administration, dans l'espace
    # de gestion (/gestion/signalements/).
    return render(request, 'foncier/signalement.html', {
        'form': form,
    })'''

nouvelle_fonction = '''def signalement(request):
    if request.method == 'POST':
        form = SignalementForm(request.POST, request.FILES)
        if form.is_valid():
            objet = form.save()
            messages.success(request, "Votre signalement a bien été enregistré. Merci pour votre contribution.")
            return redirect('signalement_confirmation', reference=objet.reference)
    else:
        form = SignalementForm()

    # Les signalements sont confidentiels : ils ne sont plus listés ici.
    # Ils sont visibles uniquement par l'administration, dans l'espace
    # de gestion (/gestion/signalements/).
    return render(request, 'foncier/signalement.html', {
        'form': form,
    })


def signalement_confirmation(request, reference):
    """Affichée juste après l'envoi d'un signalement : donne au citoyen son
    code de suivi personnel, à conserver pour vérifier l'évolution de son
    signalement plus tard, sans avoir besoin de créer de compte."""
    objet = get_object_or_404(Signalement, reference=reference)
    return render(request, 'foncier/signalement_confirmation.html', {
        'signalement': objet,
    })


def signalement_suivi(request):
    """Suivi public et anonyme d'un signalement à partir de son code de
    suivi secret (UUID) : ne montre JAMAIS la note interne de l'agent, ni
    aucune information sur les autres signalements."""
    code = request.GET.get('reference', '').strip()
    objet = None
    recherche_effectuee = bool(code)
    erreur = None

    if code:
        try:
            objet = Signalement.objects.get(reference=code)
        except (Signalement.DoesNotExist, ValueError, ValidationError):
            erreur = "Aucun signalement ne correspond à ce code. Vérifiez qu'il est bien complet."

    return render(request, 'foncier/signalement_suivi.html', {
        'code': code,
        'signalement': objet,
        'recherche_effectuee': recherche_effectuee,
        'erreur': erreur,
    })'''

erreurs = []

if ancien_import_1 in contenu:
    contenu = contenu.replace(ancien_import_1, nouveau_import_1, 1)
    print("OK  : import 'render, redirect' corrigé.")
elif nouveau_import_1 in contenu:
    print("SKIP: import déjà corrigé, rien à faire.")
else:
    erreurs.append("import 'from django.shortcuts import render, redirect' introuvable tel quel.")

if ancien_import_2 in contenu:
    contenu = contenu.replace(ancien_import_2, nouveau_import_2, 1)
    print("OK  : import 'PermissionDenied' corrigé.")
elif nouveau_import_2 in contenu:
    print("SKIP: import déjà corrigé, rien à faire.")
else:
    erreurs.append("import 'from django.core.exceptions import PermissionDenied' introuvable tel quel.")

if ancienne_fonction in contenu:
    contenu = contenu.replace(ancienne_fonction, nouvelle_fonction, 1)
    print("OK  : fonction signalement() remplacée + 2 nouvelles fonctions ajoutées.")
elif "def signalement_confirmation" in contenu:
    print("SKIP: fonctions déjà présentes, rien à faire.")
else:
    erreurs.append("fonction signalement() introuvable telle quelle (probablement déjà modifiée différemment).")

if erreurs:
    print("\n--- CE SCRIPT N'A PAS PU TOUT APPLIQUER ---")
    for e in erreurs:
        print(" - " + e)
    print("Le fichier n'a PAS été modifié pour les parties en échec. Copiez-collez le contenu de")
    print("foncier/views.py ici pour que je puisse voir la version exacte que vous avez.")
else:
    with io.open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print("\nTOUT EST OK — foncier/views.py a été mis à jour avec succès.")