# -*- coding: utf-8 -*-
"""
python manage.py shell -c "exec(open('diag_demarches5.py', encoding='utf-8').read())"

On sait deja (script precedent) :
  - 517 DemandeService au total, toutes avec type_demande__categorie == "CADASTRE"
  - 0 avec categorie == "FISCALITE"
  => c'est pour ca que la page est vide pour un Chef Fiscal : aucun type de
     demande n'est marque "FISCALITE" en base, meme les types qui sont
     manifestement fiscaux (exoneration, plan de paiement, declaration...).

Ce script retrouve le nom exact du modele "type de demande" (pour
remplacer TypeDemandeService qui n'existe pas) et liste tous les types
avec leur categorie actuelle, pour qu'on sache lesquels corriger.
"""
import foncier.models as m

candidats = [n for n in dir(m) if "type" in n.lower() and "demande" in n.lower()]
print("Classes candidates dans foncier.models :", candidats)
print()

# on prend la premiere qui a un champ 'categorie'
ModeleType = None
for nom in candidats:
    classe = getattr(m, nom)
    if hasattr(classe, "_meta"):
        champs = [f.name for f in classe._meta.get_fields()]
        if "categorie" in champs:
            ModeleType = classe
            print(f"-> Modele retenu : {nom} (champs : {champs})")
            break

if ModeleType is None:
    print("Aucune classe trouvee automatiquement avec un champ 'categorie'.")
    print("Tentative via le related model du champ type_demande de DemandeService :")
    champ = m.DemandeService._meta.get_field("type_demande")
    ModeleType = champ.related_model
    print("-> Modele retenu via relation :", ModeleType.__name__)

print()
print("Liste complete des types de demande et leur categorie :")
for t in ModeleType.objects.all().order_by("categorie", "pk"):
    nb = m.DemandeService.objects.filter(type_demande=t).count()
    libelle = getattr(t, "libelle", None) or getattr(t, "nom", None) or str(t)
    print(f"  id={t.pk:<4} categorie={t.categorie!r:<15} nb_demandes={nb:<5} libelle={libelle}")

print()
print("Script termine. Copiez-collez toute la sortie ci-dessus.")