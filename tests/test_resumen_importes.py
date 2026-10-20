import unittest
from decimal import Decimal

from src.conciliacion import conciliar_filas
from src.importes import resumir_importes


def crear_fila(identificador, importe, origen):
    if origen == "banco":
        return {
            "ID Cheque": identificador,
            "Importe": importe,
            "Fecha Pago": "19/10/2026"
        }

    return {
        "ID CHEQUE": identificador,
        "IMPORTE": importe,
        "FECHA DE COBRO": "19/10/2026"
    }


class TestResumenImportes(unittest.TestCase):

    def test_totales_y_pares_con_diferencias(self):
        banco = [
            crear_fila("ABC123", "100.00", "banco"),
            crear_fila("DEF456", "200.00", "banco")
        ]
        sistema = [
            crear_fila("ABC123", "100.00", "sistema"),
            crear_fila("DEF456", "180.00", "sistema")
        ]

        # El segundo par tiene diferencias de importe y fecha.
        sistema[1]["FECHA DE COBRO"] = "20/10/2026"

        resultados, _ = conciliar_filas(banco, sistema)
        resumen = resumir_importes(banco, sistema, resultados)

        self.assertEqual(resumen["total_banco"], Decimal("300.00"))
        self.assertEqual(resumen["total_sistema"], Decimal("280.00"))
        self.assertEqual(resumen["diferencia"], Decimal("20.00"))
        self.assertEqual(
            resumen["diferencia_absoluta"], Decimal("20.00")
        )
        self.assertEqual(
            resumen["importe_conciliado"], Decimal("100.00")
        )
        self.assertEqual(
            resumen["importe_con_diferencias_banco"],
            Decimal("200.00")
        )
        self.assertEqual(
            resumen["importe_con_diferencias_sistema"],
            Decimal("180.00")
        )

    def test_totales_iguales_no_significan_conciliacion(self):
        banco = [
            crear_fila("ABC123", "100.00", "banco"),
            crear_fila("DEF456", "200.00", "banco")
        ]
        sistema = [
            crear_fila("ABC123", "120.00", "sistema"),
            crear_fila("DEF456", "180.00", "sistema")
        ]

        resultados, _ = conciliar_filas(banco, sistema)
        resumen = resumir_importes(banco, sistema, resultados)

        self.assertEqual(resumen["diferencia"], Decimal("0.00"))
        self.assertEqual(
            resumen["importe_conciliado"], Decimal("0.00")
        )
        self.assertTrue(
            all(
                resultado["estado"] == "ERROR_IMPORTE"
                for resultado in resultados
            )
        )

    def test_duplicados_incluidos_solo_en_total_bruto(self):
        banco = [
            crear_fila("ABC123", "100.00", "banco"),
            crear_fila("ABC123", "100.00", "banco")
        ]
        sistema = [
            crear_fila("ABC123", "100.00", "sistema")
        ]

        resultados, _ = conciliar_filas(banco, sistema)
        resumen = resumir_importes(banco, sistema, resultados)

        self.assertEqual(resumen["total_banco"], Decimal("200.00"))
        self.assertEqual(
            resumen["importe_conciliado"], Decimal("0.00")
        )
        self.assertEqual(
            resumen["detalle_banco"]["duplicados_incluidos"],
            [1, 2]
        )

    def test_rechazar_resultados_incompletos_o_repetidos(self):
        banco = [
            crear_fila("ABC123", "100.00", "banco")
        ]
        sistema = [
            crear_fila("ABC123", "100.00", "sistema")
        ]

        resultados, _ = conciliar_filas(banco, sistema)

        with self.assertRaises(ValueError):
            resumir_importes(banco, sistema, [])

        repetidos = resultados + resultados

        with self.assertRaises(ValueError):
            resumir_importes(banco, sistema, repetidos)


if __name__ == "__main__":
    unittest.main()