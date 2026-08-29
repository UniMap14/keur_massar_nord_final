# ============================================================
# foncier/antispam.py
#
# Protection anti-robots légère pour les formulaires PUBLICS
# (signalement, contact, inscription, soumission de projet...),
# sans reCAPTCHA ni service externe, et sans migration de base
# de données (les champs ajoutés ne sont jamais enregistrés).
#
# Deux techniques combinées :
#
#   1. HONEYPOT : un champ invisible pour un humain (positionné
#      hors écran en CSS, jamais avec display:none — certains
#      robots l'ignorent sinon) mais qu'un robot HTTP basique
#      remplit presque toujours automatiquement. S'il est rempli
#      → on rejette silencieusement.
#
#   2. DÉLAI MINIMUM : un horodatage caché est posé au moment de
#      l'affichage du formulaire. Si le formulaire est soumis
#      moins de MIN_SUBMIT_SECONDS après son affichage, c'est
#      presque toujours un robot (un humain met toujours plus de
#      temps à lire et remplir un formulaire).
#
# UTILISATION :
#
#   from foncier.antispam import AntiSpamFormMixin
#
#   class MonFormulaire(AntiSpamFormMixin, forms.ModelForm):
#       class Meta:
#           ...
#
# IMPORTANT : le mixin doit être placé EN PREMIER dans l'héritage
# (avant forms.Form / forms.ModelForm / UserCreationForm...).
#
# Avec les templates qui font {{ form.as_p }} ou {% for field in
# form %}, les deux champs apparaissent automatiquement (invisibles).
# Avec les templates qui affichent les champs un par un par leur
# nom (ex: {{ form.email }}), il faut ajouter manuellement dans le
# <form> :
#
#   {{ form.site_web }}
#   {{ form.horodatage }}
# ============================================================

import time
from django import forms

HONEYPOT_FIELD_NAME = "site_web"
TIMESTAMP_FIELD_NAME = "horodatage"
MIN_SUBMIT_SECONDS = 2  # en dessous, on considère que c'est un robot

MESSAGE_GENERIQUE = "Une erreur est survenue lors de l'envoi. Merci de réessayer."


class AntiSpamFormMixin(forms.Form):
    """Mixin à ajouter à un formulaire public pour filtrer une bonne
    partie des soumissions automatisées (voir en-tête du fichier)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[HONEYPOT_FIELD_NAME] = forms.CharField(
            required=False,
            label="",
            widget=forms.TextInput(attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                # Hors écran plutôt que display:none : certains robots
                # basiques ignorent display:none mais pas position:absolute.
                "style": "position:absolute; left:-9999px; top:-9999px; height:0; width:0;",
                "aria-hidden": "true",
            }),
        )
        self.fields[TIMESTAMP_FIELD_NAME] = forms.CharField(
            required=False,
            widget=forms.HiddenInput(),
            initial=lambda: str(int(time.time())),
        )

    def clean(self):
        cleaned_data = super().clean()

        # 1. Honeypot rempli -> quasi certainement un robot.
        if cleaned_data.get(HONEYPOT_FIELD_NAME):
            raise forms.ValidationError(MESSAGE_GENERIQUE)

        # 2. Soumission trop rapide -> quasi certainement un robot.
        horodatage = cleaned_data.get(TIMESTAMP_FIELD_NAME)
        if horodatage:
            try:
                ecoule = time.time() - float(horodatage)
                if ecoule < MIN_SUBMIT_SECONDS:
                    raise forms.ValidationError(MESSAGE_GENERIQUE)
            except (TypeError, ValueError):
                # Horodatage absent/corrompu : on ne bloque pas un humain
                # pour ça, on laisse simplement passer.
                pass

        return cleaned_data
