CHEMIN = "foncier/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''def foncier_info(request):
    """Page publique d'information sur le systeme foncier (documents, procedures, cadre legal)."""
    return render(request, 'foncier/foncier_info.html')'''

nouveau = '''def foncier_info(request):
    """Ancienne page dediee au foncier, desormais fusionnee dans l'onglet
    'Foncier' de la page Fiscalite. Redirige vers ce nouvel emplacement."""
    return redirect('/fiscalite/#panel-foncier')'''

if "redirect('/fiscalite/#panel-foncier')" in contenu:
    print("IGNORE : redirection deja en place.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : foncier_info redirige maintenant vers l'onglet Foncier de Fiscalite.")
else:
    print("ERREUR : vue foncier_info introuvable telle quelle.")