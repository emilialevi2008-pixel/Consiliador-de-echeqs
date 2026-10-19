import unittest
from datetime import date, datetime

from src.validaciones import (
    convertir_fecha,
    mostrar_fecha,
    convertir_importe
)
from decimal import Decimal

class TestValidaciones(unittest.TestCase):

    def test_fecha_argentina(self):
        resultado = convertir_fecha("19/10/2026")

        self.assertEqual(resultado, date(2026, 10, 19))
        self.assertEqual(mostrar_fecha(resultado), "19/10/2026")

    def test_fecha_iso(self):
        resultado = convertir_fecha("2026-10-19")

        self.assertEqual(resultado, date(2026, 10, 19))

    def test_fecha_de_excel(self):
        fecha_excel = datetime(2026, 10, 19, 0, 0)

        resultado = convertir_fecha(fecha_excel)

        self.assertEqual(resultado, date(2026, 10, 19))

    def test_fecha_imposible(self):
        with self.assertRaises(ValueError):
            convertir_fecha("31/02/2026")

    def test_no_confundir_dia_y_mes(self):
        resultado = convertir_fecha("01/02/2026")

        self.assertEqual(resultado, date(2026, 2, 1))

    def test_importe_con_punto(self):
        resultado = convertir_importe("15000.50")
        self.assertEqual(resultado, Decimal("15000.50"))

    def test_importe_con_coma(self):
        resultado = convertir_importe("15000,50")
        self.assertEqual(resultado, Decimal("15000.50"))

    def test_importe_numerico_de_excel(self):
        resultado = convertir_importe(15000.50)
        self.assertEqual(resultado, Decimal("15000.50"))

    def test_importes_invalidos(self):
        valores = [None, "", "-100", "abc", "15.000,50", "1.005"]

        for valor in valores:
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    convertir_importe(valor)

    def test_suma_exacta_de_importes(self):
        primero = convertir_importe("0.10")
        segundo = convertir_importe("0.20")

        self.assertEqual(primero + segundo, Decimal("0.30"))
if __name__ == "__main__":
    unittest.main()