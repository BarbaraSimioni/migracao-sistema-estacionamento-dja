from django.test import TestCase

from api.models import Vaga


class InitialParkingSpacesTests(TestCase):
    def test_new_database_contains_exactly_the_15_initial_parking_spaces(self):
        spaces = list(
            Vaga.objects.order_by("numero").values_list(
                "numero", "tipo", "status"
            )
        )

        self.assertEqual(
            spaces,
            [
                ("A01", "CARRO", "LIVRE"),
                ("A02", "CARRO", "LIVRE"),
                ("A03", "CARRO", "LIVRE"),
                ("A04", "CARRO", "LIVRE"),
                ("A05", "CARRO", "LIVRE"),
                ("A06", "CARRO", "LIVRE"),
                ("A07", "CARRO", "LIVRE"),
                ("A08", "CARRO", "LIVRE"),
                ("A09", "CARRO", "LIVRE"),
                ("A10", "CARRO", "LIVRE"),
                ("B01", "MOTO", "LIVRE"),
                ("B02", "MOTO", "LIVRE"),
                ("B03", "MOTO", "LIVRE"),
                ("B04", "MOTO", "LIVRE"),
                ("B05", "MOTO", "LIVRE"),
            ],
        )
