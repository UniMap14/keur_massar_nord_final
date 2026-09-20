# ============================================================
# foncier/management/commands/envoyer_rappels_echeances.py
#
# Envoie des rappels automatiques (SMS + email si disponible) aux
# contribuables ayant une taxation impayée, à l'approche de la date
# limite définie sur le TypeTaxe (mois_echeance / jour_echeance) :
#
#   - 30 jours avant l'échéance
#   - 7 jours avant l'échéance
#   - le jour même de l'échéance
#   - puis un rappel de retard tous les 30 jours tant que ce n'est
#     pas payé
#
# Ne fait rien pour les TypeTaxe sans échéance configurée (mois/jour
# non renseignés dans le dashboard), ni pour les taxations déjà
# soldées. Chaque contribuable ne reçoit jamais deux rappels le même
# jour, même si la commande est relancée plusieurs fois.
#
# UTILISATION :
#   python manage.py envoyer_rappels_echeances
#
# Cette commande doit être exécutée automatiquement une fois par jour
# — voir le LISEZ-MOI fourni pour la configuration du Planificateur
# de tâches Windows (aucun cron sous Windows).
# ============================================================

import datetime

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

from foncier.models import Taxation
from foncier.sms import envoyer_sms

SEUILS_AVANT_ECHEANCE = [30, 7, 0]  # jours avant l'échéance
FREQUENCE_RAPPEL_RETARD_JOURS = 30  # une fois en retard, rappel tous les X jours


class Command(BaseCommand):
    help = "Envoie des rappels SMS/email aux contribuables dont une échéance fiscale approche ou est dépassée."

    def handle(self, *args, **options):
        aujourdhui = datetime.date.today()
        n_envoyes = 0
        n_examines = 0

        taxations = (
            Taxation.objects
            .select_related("contribuable", "type_taxe")
            .exclude(type_taxe__mois_echeance__isnull=True)
            .exclude(type_taxe__jour_echeance__isnull=True)
        )

        for taxation in taxations.iterator():
            if taxation.solde <= 0:
                continue  # déjà payée, rien à rappeler

            n_examines += 1
            date_echeance = self._date_echeance(taxation, aujourdhui)
            if date_echeance is None:
                continue  # jour du mois invalide (ex: 31 février), on ignore prudemment

            jours_restants = (date_echeance - aujourdhui).days

            if not self._doit_envoyer(jours_restants, taxation.dernier_rappel_envoye, aujourdhui):
                continue

            if self._envoyer_rappel(taxation, date_echeance, jours_restants):
                taxation.dernier_rappel_envoye = aujourdhui
                taxation.save(update_fields=["dernier_rappel_envoye"])
                n_envoyes += 1

        self.stdout.write(self.style.SUCCESS(
            f"Terminé : {n_examines} taxation(s) impayée(s) examinée(s), {n_envoyes} rappel(s) envoyé(s)."
        ))

    def _date_echeance(self, taxation, aujourdhui):
        """Date d'échéance de cette taxation pour l'année en cours."""
        try:
            return datetime.date(
                aujourdhui.year,
                taxation.type_taxe.mois_echeance,
                taxation.type_taxe.jour_echeance,
            )
        except ValueError:
            return None

    def _doit_envoyer(self, jours_restants, dernier_rappel, aujourdhui):
        if dernier_rappel == aujourdhui:
            return False  # déjà envoyé aujourd'hui (relance de la commande)

        if jours_restants in SEUILS_AVANT_ECHEANCE:
            return True

        if jours_restants < 0 and abs(jours_restants) % FREQUENCE_RAPPEL_RETARD_JOURS == 0:
            return True  # rappel périodique de retard

        return False

    def _envoyer_rappel(self, taxation, date_echeance, jours_restants):
        contribuable = taxation.contribuable
        nom_taxe = taxation.type_taxe.libelle
        montant = taxation.solde

        if jours_restants > 0:
            message = (
                f"KEUR MASSAR NORD : votre {nom_taxe} ({montant:.0f} FCFA) arrive à échéance "
                f"le {date_echeance:%d/%m/%Y}. Pensez à régulariser."
            )
        elif jours_restants == 0:
            message = (
                f"KEUR MASSAR NORD : votre {nom_taxe} ({montant:.0f} FCFA) arrive à échéance "
                f"aujourd'hui."
            )
        else:
            message = (
                f"KEUR MASSAR NORD : votre {nom_taxe} ({montant:.0f} FCFA) est en retard depuis "
                f"le {date_echeance:%d/%m/%Y}."
            )
            if taxation.type_taxe.penalite_retard:
                message += f" {taxation.type_taxe.penalite_retard}"

        envoye = False

        if contribuable.telephone:
            if envoyer_sms(contribuable.telephone, message):
                envoye = True

        # Email complémentaire si le contribuable a un compte citoyen relié.
        email = self._email_du_contribuable(contribuable)
        if email:
            try:
                send_mail(
                    subject=f"[KEUR MASSAR NORD] Échéance fiscale — {nom_taxe} {taxation.annee_fiscale}",
                    message=message,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=[email],
                    fail_silently=True,
                )
                envoye = True
            except Exception:
                pass

        return envoye

    def _email_du_contribuable(self, contribuable):
        try:
            return contribuable.profil.user.email or None
        except Exception:
            return None
