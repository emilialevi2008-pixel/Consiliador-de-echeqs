import unittest
from decimal import Decimal

from src.importes import calcular_total_archivo


class TestImportes(unittest.TestCase):

    def test_total_del_banco(self):
        filas = [
            {"ID Cheque": "ABC123", "Importe": "10.10"},
            {"ID Cheque": "DEF456", "Importe": "20.20"}
        ]

        resultado = calcular_total_archivo(filas, "banco")

        self.assertEqual(resultado["total"], Decimal("30.30"))
        self.assertEqual(resultado["incluidos"], 2)
        self.assertEqual(resultado["excluidos"], 0)

    def test_total_del_sistema(self):
        filas = [
            {"ID CHEQUE": "ABC123", "IMPORTE": "1000.00"},
            {"ID CHEQUE": "DEF456", "IMPORTE": "50,25"}
        ]

        resultado = calcular_total_archivo(filas, "sistema")

        self.assertEqual(resultado["total"], Decimal("1050.25"))
        self.assertEqual(resultado["filas_incluidas"], [1, 2])

    def test_excluir_importes_invalidos_con_motivo(self):
        valores = ["-100", "", "abc", None, "25.50"]

        filas = [
            {
                "ID Cheque": f"CHEQUE{numero}",
                "Importe": valor
            }
            for numero, valor in enumerate(valores, start=1)
        ]

        resultado = calcular_total_archivo(filas, "banco")

        self.assertEqual(resultado["total"], Decimal("25.50"))
        self.assertEqual(resultado["incluidos"], 1)
        self.assertEqual(resultado["excluidos"], 4)

        excluidos = resultado["detalle_excluidos"]

        self.assertEqual(
            [entrada["fila"] for entrada in excluidos],
            [1, 2, 3, 4]
        )
        self.assertTrue(
            all(entrada["motivo"] for entrada in excluidos)
        )

        self.assertEqual(
            resultado["incluidos"] + resultado["excluidos"],
            len(filas)
        )

    def test_duplicados_se_suman_y_se_senalan(self):
        filas = [
            {"ID Cheque": "ABC123", "Importe": "10.00"},
            {"ID Cheque": "ABC123", "Importe": "20.00"}
        ]

        resultado = calcular_total_archivo(filas, "banco")

        self.assertEqual(resultado["total"], Decimal("30.00"))
        self.assertEqual(
            resultado["duplicados_incluidos"],
            [1, 2]
        )

    def test_otros_campos_invalidos_no_excluyen_el_importe(self):
        filas = [
            {
                "ID Cheque": None,
                "Fecha Pago": "19/10/2026",
                "Importe": "10.00"
            },
            {
                "ID Cheque": "ABC123",
                "Fecha Pago": "31/02/2026",
                "Importe": "20.00"
            }
        ]

        resultado = calcular_total_archivo(filas, "banco")

        self.assertEqual(resultado["total"], Decimal("30.00"))
        self.assertEqual(resultado["incluidos"], 2)
        self.assertEqual(resultado["excluidos"], 0)

    def test_precision_decimal_del_total(self):
        filas = [
            {"ID Cheque": "ABC123", "Importe": "0.10"},
            {"ID Cheque": "DEF456", "Importe": "0.20"}
        ]

        resultado = calcular_total_archivo(filas, "banco")

        self.assertIsInstance(resultado["total"], Decimal)
        self.assertEqual(resultado["total"], Decimal("0.30"))

    def test_duplicado_con_un_importe_invalido(self):
        filas = [
            {"ID Cheque": "ABC123", "Importe": "10.00"},
            {"ID Cheque": "ABC123", "Importe": "-20.00"}
        ]

        resultado = calcular_total_archivo(filas, "banco")

        self.assertEqual(resultado["total"], Decimal("10.00"))
        self.assertEqual(resultado["excluidos"], 1)
        self.assertEqual(
            resultado["duplicados_incluidos"],
            [1]
        )


if __name__ == "__main__":
    unittest.main()