import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.conciliacion import conciliar_filas
from src.importes import resumir_importes
from src.reportes import generar_reportes


def crear_banco():
    return [{
        "ID Cheque": "ABC123XYZ",
        "Importe": "100.00",
        "Fecha Pago": "18/01/2027"
    }]


def crear_sistema(identificadores):
    return [{
        "ID CHEQUE": identificador,
        "IMPORTE": "100.00",
        "FECHA DE COBRO": "18/01/2027"
    } for identificador in identificadores]


class TestRevisionFinal(unittest.TestCase):

    def test_exacto_duplicado_impide_conciliar_otro_prefijo(self):
        banco = crear_banco()
        banco.append({
            "ID Cheque": "OTRO456",
            "Importe": "100.00",
            "Fecha Pago": "18/01/2027"
        })
        sistema = crear_sistema([
            "ABC123XYZ", "ABC123XYZ", "ABC123"
        ])

        resultados, _ = conciliar_filas(banco, sistema)
        estados = [fila["estado"] for fila in resultados]

        self.assertNotIn("CONCILIADO_ID_ABREVIADO", estados)
        self.assertEqual(estados.count("ID_DUPLICADO"), 2)
        self.assertEqual(estados.count("PENDIENTE_REVISION"), 2)

    def test_exacto_unico_tiene_prioridad_sobre_prefijo_duplicado(self):
        banco = crear_banco()
        sistema = crear_sistema([
            "ABC123", "ABC123", "ABC123XYZ"
        ])

        resultados, _ = conciliar_filas(banco, sistema)
        estados = [fila["estado"] for fila in resultados]

        self.assertEqual(estados.count("CONCILIADO"), 1)
        self.assertEqual(estados.count("ID_DUPLICADO"), 2)

    def test_json_conserva_el_importe_original_rechazado(self):
        banco = crear_banco()
        banco[0]["Importe"] = Decimal("1.005")

        resultados, auditoria = conciliar_filas(banco, [])
        importes = resumir_importes(banco, [], resultados)

        with tempfile.TemporaryDirectory() as temporal:
            generar_reportes(
                temporal, resultados, auditoria, importes
            )

            ruta = Path(temporal) / "resumen.json"

            with open(ruta, encoding="utf-8") as archivo:
                resumen = json.load(archivo)

        original = resumen["auditoria"][0]["original"]["Importe"]

        excluidos = resumen["importes"]["detalle_banco"][
            "detalle_excluidos"
        ]

        self.assertEqual(original, "1.005")
        self.assertEqual(
            excluidos[0]["importe_original"], "1.005"
        )
        self.assertEqual(
            resumen["importes"]["total_banco"], "0.00"
        )


if __name__ == "__main__":
    unittest.main()