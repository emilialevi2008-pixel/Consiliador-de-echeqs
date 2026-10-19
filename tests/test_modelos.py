import unittest
from datetime import date
from decimal import Decimal

from src.modelos import ChequeElectronico


class TestChequeElectronico(unittest.TestCase):

    def test_cheques_sin_diferencias(self):
        banco = ChequeElectronico(
            "MKX9R4GYWZK9O6W",
            Decimal("15000.50"),
            date(2026, 10, 19)
        )

        sistema = ChequeElectronico(
            "MKX9R4GY",
            Decimal("15000.50"),
            date(2026, 10, 19)
        )

        self.assertEqual(banco.diferencias(sistema), [])

    def test_diferencias_de_importe_y_fecha(self):
        banco = ChequeElectronico(
            "MKX9R4GYWZK9O6W",
            Decimal("15000.50"),
            date(2026, 10, 19)
        )

        sistema = ChequeElectronico(
            "MKX9R4GY",
            Decimal("14000.50"),
            date(2026, 10, 20)
        )

        self.assertEqual(
            banco.diferencias(sistema),
            ["ERROR_IMPORTE", "ERROR_FECHA"]
        )

        self.assertEqual(
            banco.diferencia_importe(sistema),
            Decimal("1000.00")
        )

    def test_importe_negativo(self):
        with self.assertRaises(ValueError):
            ChequeElectronico(
                "MKX9R4GY",
                Decimal("-100.00"),
                date(2026, 10, 19)
            )

    def test_precision_decimal(self):
        banco = ChequeElectronico(
            "MKX9R4GY",
            Decimal("0.30"),
            date(2026, 10, 19)
        )

        sistema = ChequeElectronico(
            "MKX9R4GY",
            Decimal("0.10") + Decimal("0.20"),
            date(2026, 10, 19)
        )

        self.assertEqual(
            banco.diferencia_importe(sistema),
            Decimal("0.00")
        )


if __name__ == "__main__":
    unittest.main()