CHEMIN = "citoyens/views.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            try:
                _envoyer_email_demande_recue(request, demande)
            except Exception:
                messages.warning(
                    request,
                    "Votre demande a été enregistrée, mais l'email de confirmation n'a pas pu être envoyé."
                )
            try:
                _envoyer_email_notif_agents_demande(request, demande)
            except Exception:
                pass
            messages.success(
                request,
                f"Votre demande a bien été enregistrée sous le numéro {demande.numero_dossier}. "
                f"Vous pouvez suivre son avancement depuis « Mes démarches »."
            )
            return redirect("citoyen_demandes")'''

nouveau = '''            demande = form.save(commit=False)
            demande.demandeur = request.user
            if demande.type_demande.tarif and demande.type_demande.tarif > 0:
                demande.statut_paiement = "EN_ATTENTE"
            demande.save()
            try:
                _envoyer_email_demande_recue(request, demande)
            except Exception:
                messages.warning(
                    request,
                    "Votre demande a été enregistrée, mais l'email de confirmation n'a pas pu être envoyé."
                )
            try:
                _envoyer_email_notif_agents_demande(request, demande)
            except Exception:
                pass

            if demande.type_demande.tarif and demande.type_demande.tarif > 0:
                messages.success(
                    request,
                    f"Votre demande a bien été enregistrée sous le numéro {demande.numero_dossier}. "
                    f"Cette démarche est payante ({demande.type_demande.tarif:.0f} FCFA) — réglez-la pour lancer son traitement."
                )
                return redirect("citoyen_demande_payer", pk=demande.pk)

            messages.success(
                request,
                f"Votre demande a bien été enregistrée sous le numéro {demande.numero_dossier}. "
                f"Vous pouvez suivre son avancement depuis « Mes démarches »."
            )
            return redirect("citoyen_demandes")'''

if nouveau in contenu:
    print("DEJA FAIT : deja modifie.")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : demande_creer_view redirige maintenant vers le paiement si tarif > 0.")
else:
    print("ERREUR : bloc exact introuvable.")