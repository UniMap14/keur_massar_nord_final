# ============================================================
# foncier/tests/test_antispam.py
#
# Vérifie que le honeypot (foncier/antispam.py) bloque bien les
# soumissions automatisées (champ piège rempli, ou envoi trop rapide),
# sans jamais bloquer un envoi humain normal.
# ============================================================

import time

from django.test import TestCase

from foncier.forms import SignalementForm


def donnees_signalement_valides():
    return {
        "titre": "Nid de poule dangereux",
        "description": "Sur la route principale",
        "lieu": "Unité 12",
        "site_web": "",  # honeypot laissé vide, comme un humain le ferait
        "horodatage": str(int(time.time()) - 5),  # affiché il y a 5s, envoi humain plausible
    }


class AntiSpamHoneypotTest(TestCase):
    def test_formulaire_valide_quand_honeypot_vide_et_delai_correct(self):
        form = SignalementForm(data=donnees_signalement_valides())
        self.assertTrue(form.is_valid(), form.errors)

    def test_formulaire_rejete_si_honeypot_rempli(self):
        donnees = donnees_signalement_valides()
        donnees["site_web"] = "http://spam.example.com"
        form = SignalementForm(data=donnees)
        self.assertFalse(form.is_valid())

    def test_formulaire_rejete_si_envoi_trop_rapide(self):
        donnees = donnees_signalement_valides()
        donnees["horodatage"] = str(int(time.time()))  # affiché et soumis à la même seconde
        form = SignalementForm(data=donnees)
        self.assertFalse(form.is_valid())
