# Tâches automatiques — KMS Nord

Ce projet a deux commandes qui doivent tourner **automatiquement, sans
intervention manuelle**, une fois le site en production réelle. Sous
Windows, il n'y a pas de `cron` comme sous Linux : on utilise le
**Planificateur de tâches** (intégré à Windows).

---

## 1. Les deux commandes concernées

| Commande | Fréquence | Rôle |
|---|---|---|
| `python manage.py envoyer_rappels_echeances` | **Tous les jours** | Envoie les SMS/email de rappel (30j avant, 7j avant, le jour J, puis tous les 30j en retard) |
| `python manage.py emettre_role_annuel` | **Une fois par an** (début janvier, par exemple) | Émet automatiquement la taxation de la nouvelle année pour chaque bien déjà taxé, sans y toucher manuellement |

Les deux sont **rejouables sans risque** : les relancer plusieurs fois
le même jour ne double jamais un envoi ou une création.

---

## 2. Créer un fichier .bat pour chaque commande

Le Planificateur de tâches Windows lance des fichiers `.bat`, pas
directement des commandes Python. Créez ces 2 fichiers à la racine du
projet (à côté de `manage.py`) :

### `lancer_rappels_echeances.bat`
```bat
@echo off
cd /d C:\Users\DELL\Desktop\projet_kmsn\projet_kms\kmsn
call venv\Scripts\activate.bat
python manage.py envoyer_rappels_echeances
```

### `lancer_role_annuel.bat`
```bat
@echo off
cd /d C:\Users\DELL\Desktop\projet_kmsn\projet_kms\kmsn
call venv\Scripts\activate.bat
python manage.py emettre_role_annuel
```

**Adaptez le chemin** (`cd /d ...`) si le projet est déplacé ailleurs.

---

## 3. Configurer le Planificateur de tâches Windows

Pour **chacun** des 2 fichiers `.bat` ci-dessus :

1. Ouvrez le **Planificateur de tâches** (recherchez "Planificateur de
   tâches" dans le menu Démarrer)
2. Cliquez **"Créer une tâche de base..."** (panneau de droite)
3. **Nom** : `KMSN - Rappels échéances` (ou `KMSN - Rôle annuel`)
4. **Déclencheur** :
   - Rappels échéances → **Quotidiennement**, à une heure creuse (ex : 6h00 du matin)
   - Rôle annuel → **Annuellement**, le 1er janvier à 6h00 du matin
5. **Action** : "Démarrer un programme"
   - Programme/script : chemin complet vers le fichier `.bat`
     (ex : `C:\Users\DELL\Desktop\projet_kmsn\projet_kms\kmsn\lancer_rappels_echeances.bat`)
6. Cochez **"Ouvrir la boîte de dialogue Propriétés..."** avant de
   terminer, puis dans l'onglet **Général**, cochez **"Exécuter que
   l'utilisateur soit connecté ou non"** (sinon la tâche ne se lance
   pas si personne n'est connecté sur le PC/serveur)
7. Validez, entrez le mot de passe Windows si demandé

---

## 4. Vérifier que ça fonctionne

Dans le Planificateur de tâches, clic droit sur la tâche → **"Exécuter"**
pour la déclencher manuellement tout de suite, puis vérifiez :
- L'onglet **"Historique"** de la tâche (doit indiquer "Terminé (0x0)")
- Le terminal/log de sortie si configuré, ou simplement le résultat
  attendu (SMS/email en console, ou nouvelles taxations créées)

---

## 5. En production réelle (hébergement, pas votre PC)

Si le site est un jour déployé sur un vrai serveur (Render, Railway...)
plutôt que sur ce PC, le Planificateur de tâches Windows ne s'applique
plus : il faudra utiliser l'équivalent de l'hébergeur (ex : "Cron Jobs"
sur Render), avec les mêmes 2 commandes et les mêmes fréquences.
