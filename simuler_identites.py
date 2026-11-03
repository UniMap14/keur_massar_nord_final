# -*- coding: utf-8 -*-
import random
from citoyens.models import Citoyen

random.seed(42)

prenoms_h = ['Mamadou','Ibrahima','Moussa','Ousmane','Abdoulaye','Cheikh','Modou','Alioune','Babacar','Amadou','Souleymane','Pape','Oumar','Idrissa','Mor','Malick','Serigne','Bassirou','Lamine','Yankhoba']
prenoms_f = ['Fatou','Aissatou','Awa','Ndeye','Khady','Mariama','Aminata','Coumba','Astou','Bineta','Mame','Sokhna','Adama','Rokhaya','Diarra','Fatimata','Dieynaba','Nogaye','Yacine','Maimouna']
noms = ['Ndiaye','Diop','Fall','Sow','Diallo','Ba','Gueye','Sarr','Seck','Mbaye','Cisse','Toure','Faye','Niang','Sy','Diagne','Kane','Thiam','Diouf','Sene','Camara','Dieng','Sakho','Wade','Gning','Dabo','Ndoye','Diatta','Coly','Mendy']

operateurs = ['77','78','76','70','75']

citoyens = list(Citoyen.objects.select_related('user').all())
mis_a_jour = 0

for c in citoyens:
    est_homme = random.random() < 0.5
    prenom = random.choice(prenoms_h if est_homme else prenoms_f)
    nom = random.choice(noms)

    u = c.user
    u.first_name = prenom
    u.last_name = nom
    u.save(update_fields=['first_name', 'last_name'])

    numero = "{}{}".format(random.choice(operateurs), random.randint(1000000, 9999999))
    c.telephone = numero
    c.save(update_fields=['telephone'])

    mis_a_jour += 1

print('Citoyens mis a jour :', mis_a_jour)
print()
print('=== Exemple (5 premiers) ===')
for c in Citoyen.objects.select_related('user')[:5]:
    print(c.pk, '|', c.user.first_name, c.user.last_name, '| tel:', c.telephone, '| email:', c.user.email)