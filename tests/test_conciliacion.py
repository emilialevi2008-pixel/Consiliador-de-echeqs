import unittest

from src.pipeline import preparar_filas
from src.conciliacion import (
    conciliar_preparados,
    resultado_rechazado,
    indexar_ids_rechazados,
    conciliar_filas
)

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

    def test_resultado_de_fila_bancaria_rechazada(self):
        filas = [
            {
                "ID Cheque": "ABC123",
                "Fecha Pago": "19/10/2026",
                "Importe": "-100.00"
            }
        ]

        preparados, registro = preparar_filas(filas, "banco")
        resultado = resultado_rechazado(registro[0])

        self.assertEqual(preparados, [])
        self.assertEqual(resultado["estado"], "DATOS_INVALIDOS")
        self.assertEqual(resultado["id_banco"], "ABC123")
        self.assertEqual(resultado["importe_banco"], "-100.00")
        self.assertEqual(resultado["fila_banco"], 1)
        self.assertEqual(resultado["fila_sistema"], "")
        self.assertEqual(resultado["diferencia_importe"], "")
        self.assertIn("negativo", resultado["descripcion"])

    def test_resultado_rechazado_con_columna_faltante(self):
        fila = {
            "ID CHEQUE": "MKX9R4GY",
            "IMPORTE": "0.00"
        }

        copia = fila.copy()

        preparados, registro = preparar_filas(
            [fila], "sistema"
        )

        resultado = resultado_rechazado(registro[0])

        self.assertEqual(preparados, [])
        self.assertEqual(resultado["id_sistema"], "MKX9R4GY")
        self.assertEqual(resultado["importe_sistema"], "0.00")
        self.assertEqual(resultado["fecha_sistema"], "")
        self.assertEqual(resultado["fila_sistema"], 1)
        self.assertIn("FECHA DE COBRO", resultado["descripcion"])
        self.assertEqual(fila, copia)
    def test_indexar_ids_rechazados_y_conservar_sus_filas(self):
        filas = [
            {
                "ID Cheque": "ABC123",
                "Fecha Pago": "19/10/2026",
                "Importe": "100"
            },
            {
                "ID Cheque": " MKX9R4GYWZK9O6W ",
                "Fecha Pago": "19/10/2026",
                "Importe": "-100"
            },
            {
                "ID Cheque": "MKX9R4GYWZK9O6W",
                "Fecha Pago": "31/02/2026",
                "Importe": "100"
            }
        ]

        preparados, registro = preparar_filas(filas, "banco")

        indice = indexar_ids_rechazados(registro, "banco")

        self.assertEqual(len(preparados), 1)
        self.assertEqual(
            indice,
            {"MKX9R4GYWZK9O6W": [2, 3]}
        )
        self.assertNotIn("ABC123", indice)

    def test_no_inventar_ids_ni_mezclar_origenes(self):
        filas = [
            {
                "ID CHEQUE": None,
                "FECHA DE COBRO": "19/10/2026",
                "IMPORTE": "100"
            },
            {
                "ID CHEQUE": "???",
                "FECHA DE COBRO": "19/10/2026",
                "IMPORTE": "100"
            },
            {
                "ID CHEQUE": "SISTEMA123",
                "FECHA DE COBRO": "19/10/2026",
                "IMPORTE": "-100"
            }
        ]

        preparados, registro = preparar_filas(filas, "sistema")

        self.assertEqual(preparados, [])
        self.assertEqual(len(registro), 3)

        self.assertEqual(
            indexar_ids_rechazados(registro, "sistema"),
            {"SISTEMA123": [3]}
        )

        self.assertEqual(
            indexar_ids_rechazados(registro, "banco"),
            {}
        )
    def crear_fila(self, identificador, origen, importe="100.00"):
        """Crea una fila ficticia para estas pruebas."""

        if origen == "banco":
            return {
                "ID Cheque": identificador,
                "Fecha Pago": "19/10/2026",
                "Importe": importe
            }

        return {
            "ID CHEQUE": identificador,
            "FECHA DE COBRO": "19/10/2026",
            "IMPORTE": importe
        }

    def test_rechazado_no_fabrica_un_prefijo_unico(self):
        banco = [
            self.crear_fila("MKX9R4GY111", "banco"),
            self.crear_fila("MKX9R4GY222", "banco", "-100")
        ]
        sistema = [
            self.crear_fila("MKX9R4GY", "sistema")
        ]

        resultados, _ = conciliar_filas(banco, sistema)
        estados = [r["estado"] for r in resultados]

        self.assertIn("COINCIDENCIA_AMBIGUA", estados)
        self.assertIn("DATOS_INVALIDOS", estados)
        self.assertNotIn("CONCILIADO_ID_ABREVIADO", estados)

    def test_duplicado_bancario_con_una_fila_rechazada(self):
        banco = [
            self.crear_fila("ABC123", "banco"),
            self.crear_fila("ABC123", "banco", "-100")
        ]
        sistema = [
            self.crear_fila("ABC123", "sistema")
        ]

        resultados, _ = conciliar_filas(banco, sistema)

        duplicados = [
            r for r in resultados
            if "ID_DUPLICADO" in r["tipo_error"].split("|")
        ]

        self.assertEqual(len(duplicados), 2)
        self.assertFalse(
            any(r["estado"].startswith("CONCILIADO")
                for r in resultados)
        )

    def test_contraparte_invalida_no_se_informa_como_ausente(self):
        banco = [
            self.crear_fila("ABC123", "banco")
        ]
        sistema = [
            self.crear_fila("ABC123", "sistema", "-100")
        ]

        resultados, _ = conciliar_filas(banco, sistema)
        estados = {r["estado"] for r in resultados}

        self.assertEqual(
            estados,
            {"PENDIENTE_REVISION", "DATOS_INVALIDOS"}
        )

    def test_exacto_valido_no_se_bloquea_por_otro_id(self):
        banco = [
            self.crear_fila("MKX9R4GY", "banco"),
            self.crear_fila("MKX9R4GY999", "banco", "-100")
        ]
        sistema = [
            self.crear_fila("MKX9R4GY", "sistema")
        ]

        resultados, _ = conciliar_filas(banco, sistema)
        estados = [r["estado"] for r in resultados]

        self.assertEqual(estados.count("CONCILIADO"), 1)
        self.assertEqual(estados.count("DATOS_INVALIDOS"), 1)

    def test_rechazados_sin_id_conservan_sus_filas(self):
        banco = [
            self.crear_fila(None, "banco")
        ]
        sistema = [
            self.crear_fila("???", "sistema")
        ]

        resultados, auditoria = conciliar_filas(banco, sistema)

        self.assertEqual(len(resultados), 2)
        self.assertEqual(len(auditoria), 2)

        filas_banco = [
            r["fila_banco"] for r in resultados
            if r["fila_banco"] != ""
        ]
        filas_sistema = [
            r["fila_sistema"] for r in resultados
            if r["fila_sistema"] != ""
        ]

        self.assertEqual(filas_banco, [1])
        self.assertEqual(filas_sistema, [1])

    def test_duplicado_contable_con_una_fila_rechazada(self):
        banco = [
            self.crear_fila("ABC123", "banco")
        ]
        sistema = [
            self.crear_fila("ABC123", "sistema"),
            self.crear_fila("ABC123", "sistema", "-100")
        ]

        resultados, _ = conciliar_filas(banco, sistema)

        duplicados = [
            r for r in resultados
            if "ID_DUPLICADO" in r["tipo_error"].split("|")
        ]

        self.assertEqual(len(duplicados), 2)
        self.assertIn(
            "PENDIENTE_REVISION",
            [r["estado"] for r in resultados]
        )

    def test_exacto_invalido_no_se_reemplaza_por_un_prefijo(self):
        banco = [
            self.crear_fila("ABC123", "banco", "-100"),
            self.crear_fila("ABC123XYZ", "banco")
        ]
        sistema = [
            self.crear_fila("ABC123", "sistema")
        ]

        resultados, _ = conciliar_filas(banco, sistema)

        self.assertFalse(
            any(r["estado"].startswith("CONCILIADO")
                for r in resultados)
        )

        resultado_sistema = [
            r for r in resultados
            if r["fila_sistema"] == 1
        ]

        self.assertEqual(
            resultado_sistema[0]["estado"],
            "PENDIENTE_REVISION"
        )
        
if __name__ == "__main__":
    unittest.main()