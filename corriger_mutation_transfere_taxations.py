CHEMIN = "foncier/dashboard_views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''            demande.statut = DemandeMutation.STATUT_VALIDEE
            demande.nouveau_contribuable_cree = nouveau_contribuable
            demande.traite_par = request.user
            demande.date_traitement = timezone.now()
            demande.save()'''

nouveau = '''            # Transfere les taxations EXISTANTES de cette parcelle au
            # nouveau contribuable, pour que la parcelle disparaisse de
            # "Ma fiscalite" chez l'ancien proprietaire (historique de
            # paiement conserve, seul le titulaire change).
            Taxation.objects.filter(parcelle=demande.parcelle).update(
                contribuable=nouveau_contribuable
            )

            demande.statut = DemandeMutation.STATUT_VALIDEE
            demande.nouveau_contribuable_cree = nouveau_contribuable
            demande.traite_par = request.user
            demande.date_traitement = timezone.now()
            demande.save()'''

if "Transfere les taxations EXISTANTES" in contenu:
    print("DEJA FAIT : deja corrige.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : les taxations existantes sont maintenant transferees au nouveau proprietaire.")
else:
    print("ERREUR : bloc exact introuvable.")