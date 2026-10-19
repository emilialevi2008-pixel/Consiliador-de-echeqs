import unittest
from datetime import date
from decimal import Decimal

from src.pipeline import convertir_fila


class TestPipeline(unittest.TestCase):

    def test_convertir_fila_banco(self):
        fila = {
            "ID Cheque": "MKX9R4GYWZK9O6W",
            "Fecha Pago": "19/10/2026",
            "Importe": "15000,50"
        }

        cheque = convertir_fila(fila, "banco")

        self.assertEqual(cheque.identificador, "MKX9R4GYWZK9O6W")
        self.assertEqual(cheque.importe, Decimal("15000.50"))
        self.assertEqual(cheque.fecha_pago, date(2026, 10, 19))

    def test_convertir_fila_sistema(self):
        fila = {
            "ID CHEQUE": "MKX9R4GY",
            "FECHA DE COBRO": "2026-10-19",
            "IMPORTE": "15000.50"
        }

        cheque = convertir_fila(fila, "sistema")

        self.assertEqual(cheque.identificador, "MKX9R4GY")
        self.assertEqual(cheque.importe, Decimal("15000.50"))
        self.assertEqual(cheque.fecha_pago, date(2026, 10, 19))

    def test_columna_obligatoria_faltante(self):
        fila = {
            "ID Cheque": "MKX9R4GYWZK9O6W",
            "Importe": "15000.50"
        }

        with self.assertRaisesRegex(ValueError, "Fecha Pago"):
            convertir_fila(fila, "banco")

    def test_origen_incorrecto(self):
        with self.assertRaises(ValueError):
            convertir_fila({}, "otro")


if __name__ == "__main__":
    unittest.main()