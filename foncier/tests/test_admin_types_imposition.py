from django.test import TestCase

from citoyens.forms import DeclarationFiscaleForm
from foncier.dashboard_views import TaxationForm
from foncier.models import TypeTaxe


class TypesImpositionAdminTest(TestCase):
    def test_quatre_types_sont_disponibles_pour_une_nouvelle_taxation(self):
        codes_attendus = {"CFPB", "CFPNB", "IRF", "TEOM"}
        codes_disponibles = set(
            TaxationForm().fields["type_taxe"].queryset.values_list("code", flat=True)
        )

        self.assertEqual(codes_disponibles, codes_attendus)

    def test_declaration_parcelle_ne_propose_que_cfpb_et_cfpnb(self):
        TypeTaxe.objects.create(code="FONCIERE", libelle="Ancienne taxe foncière")
        codes_disponibles = set(
            DeclarationFiscaleForm().fields["type_taxe"].queryset.values_list("code", flat=True)
        )

        self.assertEqual(codes_disponibles, {"CFPB", "CFPNB"})
