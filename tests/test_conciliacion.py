import unittest

from src.pipeline import preparar_filas
from src.conciliacion import conciliar_preparados


def conciliar_ids(ids_banco, ids_sistema):
    """Prepara datos ficticios para las pruebas."""

    filas_banco = [
        {
            "ID Cheque": codigo,
            "Fecha Pago": "19/10/2026",
            "Importe": "15000.50"
        }
        for codigo in ids_banco
    ]

    filas_sistema = [
        {
            "ID CHEQUE": codigo,
            "FECHA DE COBRO": "19/10/2026",
            "IMPORTE": "15000.50"
        }
        for codigo in ids_sistema
    ]

    banco, _ = preparar_filas(filas_banco, "banco")
    sistema, _ = preparar_filas(filas_sistema, "sistema")

    return conciliar_preparados(banco, sistema)


class TestConciliacion(unittest.TestCase):

    def test_coincidencia_exacta(self):
        resultados = conciliar_ids(
            ["ABC123"],
            ["ABC123"]
        )

        self.assertEqual(len(resultados), 1)
        self.assertEqual(
            resultados[0]["estado"],
            "CONCILIADO"
        )

    def test_coincidencia_abreviada(self):
        resultados = conciliar_ids(
            ["MKX9R4GYWZK9O6W"],
            ["MKX9R4GY"]
        )

        self.assertEqual(len(resultados), 1)
        self.assertEqual(
            resultados[0]["estado"],
            "CONCILIADO_ID_ABREVIADO"
        )

    def test_prefijo_con_varios_candidatos(self):
        resultados = conciliar_ids(
            ["MKX9R4GY111", "MKX9R4GY222"],
            ["MKX9R4GY"]
        )

        estados = [r["estado"] for r in resultados]

        self.assertEqual(
            estados.count("COINCIDENCIA_AMBIGUA"), 1
        )
        self.assertEqual(
            estados.count("PENDIENTE_REVISION"), 2
        )

    def test_duplicados_del_banco(self):
        resultados = conciliar_ids(
            ["ABC123", "ABC123"],
            ["ABC123"]
        )

        estados = [r["estado"] for r in resultados]

        self.assertEqual(estados.count("ID_DUPLICADO"), 2)
        self.assertNotIn("CONCILIADO", estados)

    def test_duplicados_del_sistema(self):
        resultados = conciliar_ids(
            ["ABC123"],
            ["ABC123", "ABC123"]
        )

        estados = [r["estado"] for r in resultados]

        self.assertEqual(estados.count("ID_DUPLICADO"), 2)
        self.assertEqual(
            estados.count("PENDIENTE_REVISION"), 1
        )

    def test_exacto_tiene_prioridad_sobre_abreviado(self):
        resultados = conciliar_ids(
            ["MKX9R4GYWZK9O6W"],
            ["MKX9R4GY", "MKX9R4GYWZK9O6W"]
        )

        conciliados = [
            r for r in resultados
            if r["estado"] == "CONCILIADO"
        ]

        self.assertEqual(len(conciliados), 1)
        self.assertEqual(
            conciliados[0]["id_sistema"],
            "MKX9R4GYWZK9O6W"
        )
        self.assertEqual(len(resultados), 2)

    def test_dos_prefijos_compiten_por_el_mismo_banco(self):
        resultados = conciliar_ids(
            ["MKX9R4GYWZK9O6W"],
            ["MKX9R4", "MKX9R4GY"]
        )

        estados = [r["estado"] for r in resultados]

        self.assertEqual(
            estados.count("COINCIDENCIA_AMBIGUA"), 2
        )
        self.assertEqual(
            estados.count("PENDIENTE_REVISION"), 1
        )
        self.assertNotIn("CONCILIADO_ID_ABREVIADO", estados)

    def test_cheques_sin_correspondencia(self):
        resultados = conciliar_ids(
            ["ABC123"],
            ["XYZ789"]
        )

        estados = {r["estado"] for r in resultados}

        self.assertEqual(
            estados,
            {"NO_ESTA_EN_BANCO", "NO_ESTA_EN_SISTEMA"}
        )

    def test_cada_fila_aparece_una_sola_vez(self):
        resultados = conciliar_ids(
            ["ABC123", "DEF456", "GHI789"],
            ["ABC123", "DEF", "XYZ999"]
        )

        filas_banco = [
            r["fila_banco"] for r in resultados
            if r["fila_banco"] != ""
        ]

        filas_sistema = [
            r["fila_sistema"] for r in resultados
            if r["fila_sistema"] != ""
        ]

        self.assertEqual(sorted(filas_banco), [1, 2, 3])
        self.assertEqual(sorted(filas_sistema), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()