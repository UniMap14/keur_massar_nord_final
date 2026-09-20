CHEMIN = "foncier/paiement_gateway.py"

with open(CHEMIN, encoding="utf-8") as f:
    contenu = f.read()

ancien = '''        paiement = Paiement.objects.create(
            taxation=taxation,
            montant=montant,
            mode_paiement='MOBILE',
            statut_paiement='CONFIRME',
            reference_transaction=f"DEMO-{uuid.uuid4().hex[:10].upper()}",
        )'''

nouveau = '''        paiement = Paiement.objects.create(
            taxation=taxation,
            montant=montant,
            mode_paiement='MOBILE',
            statut_paiement='EN_ATTENTE',
            reference_transaction=f"DEMO-{uuid.uuid4().hex[:10].upper()}",
        )'''

if nouveau in contenu:
    print("DEJA FAIT : deja corrige (verifie precisement).")
elif ancien in contenu:
    contenu = contenu.replace(ancien, nouveau, 1)
    with open(CHEMIN, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
    print("OK : le paiement manuel est maintenant 'En attente' jusqu'a validation par un agent.")
else:
    print("ERREUR : bloc exact introuvable.")