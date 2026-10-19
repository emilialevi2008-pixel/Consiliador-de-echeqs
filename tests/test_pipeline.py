import unittest
from datetime import date
from decimal import Decimal

from src.pipeline import convertir_fila, preparar_filas


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
    def test_preparar_filas_con_un_rechazo(self):
        filas = [
            {
                "ID Cheque": "MKX9R4GYWZK9O6W",
                "Fecha Pago": "19/10/2026",
                "Importe": "15000.50"
            },
            {
                "ID Cheque": "ABC123",
                "Fecha Pago": "19/10/2026",
                "Importe": "-100.00"
            }
        ]

        preparados, registro = preparar_filas(filas, "banco")

        self.assertEqual(len(preparados), 1)
        self.assertEqual(preparados[0]["fila"], 1)

        rechazadas = [
            entrada for entrada in registro
            if entrada["estado"] == "rechazada"
        ]

        self.assertEqual(len(rechazadas), 1)
        self.assertEqual(rechazadas[0]["fila"], 2)
        self.assertIn("negativo", rechazadas[0]["motivo"])

        self.assertEqual(
            len(preparados) + len(rechazadas),
            len(filas)
        )

    def test_registrar_cambios_sin_alterar_original(self):
        fila = {
            "ID CHEQUE": " MKX9R4GY ",
            "FECHA DE COBRO": "2026-10-19",
            "IMPORTE": "15000,50"
        }

        copia = fila.copy()

        preparados, registro = preparar_filas(
            [fila], "sistema"
        )

        self.assertEqual(fila, copia)
        self.assertEqual(len(preparados), 1)
        self.assertEqual(len(registro), 1)

        cambios = registro[0]["cambios"]

        self.assertEqual(
            cambios["ID CHEQUE"]["despues"],
            "MKX9R4GY"
        )
        self.assertEqual(
            cambios["FECHA DE COBRO"]["despues"],
            "19/10/2026"
        )
        self.assertEqual(
            cambios["IMPORTE"]["despues"],
            "15000.50"
        )

if __name__ == "__main__":
    unittest.main()