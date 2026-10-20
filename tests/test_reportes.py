import csv
import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.conciliacion import conciliar_filas
from src.importes import resumir_importes
from src.reportes import generar_reportes


class TestReportes(unittest.TestCase):

    def test_generar_y_leer_los_cuatro_reportes(self):
        banco = [
            {
                "ID Cheque": "ABC123",
                "Importe": Decimal("100.10"),
                "Fecha Pago": date(2026, 10, 19)
            },
            {
                "ID Cheque": "DEF456",
                "Importe": "200.00",
                "Fecha Pago": "19/10/2026"
            },
            {
                "ID Cheque": "ERR789",
                "Importe": None,
                "Fecha Pago": "19/10/2026"
            }
        ]

        sistema = [
            {
                "ID CHEQUE": "ABC123",
                "IMPORTE": "100.10",
                "FECHA DE COBRO": "19/10/2026"
            },
            {
                "ID CHEQUE": "DEF456",
                "IMPORTE": "180.00",
                "FECHA DE COBRO": "19/10/2026"
            }
        ]

        resultados, auditoria = conciliar_filas(banco, sistema)
        importes = resumir_importes(banco, sistema, resultados)

        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal) / "salidas"

            generar_reportes(
                carpeta, resultados, auditoria, importes
            )

            nombres = {
                archivo.name for archivo in carpeta.iterdir()
            }

            self.assertEqual(nombres, {
                "reporte_conciliacion.csv",
                "cheques_con_errores.csv",
                "resumen.json",
                "resumen_importes.csv"
            })

            with open(
                carpeta / "reporte_conciliacion.csv",
                encoding="utf-8-sig",
                newline=""
            ) as archivo:
                reporte = list(csv.DictReader(archivo))

            self.assertEqual(len(reporte), 3)
            self.assertEqual(
                {fila["estado"] for fila in reporte},
                {"CONCILIADO", "ERROR_IMPORTE", "DATOS_INVALIDOS"}
            )

            with open(
                carpeta / "cheques_con_errores.csv",
                encoding="utf-8-sig",
                newline=""
            ) as archivo:
                errores = list(csv.DictReader(archivo))

            self.assertEqual(len(errores), 2)
            self.assertTrue(
                all(fila["estado"] != "CONCILIADO" for fila in errores)
            )

            with open(
                carpeta / "resumen.json",
                encoding="utf-8"
            ) as archivo:
                resumen = json.load(archivo)

            self.assertEqual(
                resumen["importes"]["total_banco"], "300.10"
            )
            self.assertEqual(
                resumen["importes"]["total_sistema"], "280.10"
            )
            self.assertEqual(
                resumen["importes"]["importe_conciliado"], "100.10"
            )

            rechazos = [
                entrada
                for entrada in resumen["auditoria"]
                if entrada["estado"] == "rechazada"
            ]

            self.assertEqual(len(rechazos), 1)
            self.assertIsNone(rechazos[0]["original"]["Importe"])

            conversiones = [
                entrada
                for entrada in resumen["auditoria"]
                if entrada["estado"] == "modificada"
            ]

            self.assertEqual(
                conversiones[0]["original"]["Fecha Pago"],
                "19/10/2026"
            )
            self.assertEqual(
                conversiones[0]["original"]["Importe"],
                "100.10"
            )

            with open(
                carpeta / "resumen_importes.csv",
                encoding="utf-8-sig",
                newline=""
            ) as archivo:
                filas_importes = list(csv.DictReader(archivo))

            valores = {
                fila["concepto"]: fila["importe"]
                for fila in filas_importes
            }

            self.assertEqual(
                valores["Diferencia: banco menos sistema"], "20.00"
            )

    def test_reporte_sin_errores_conserva_encabezados(self):
        importes = resumir_importes([], [], [])

        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)

            generar_reportes(carpeta, [], [], importes)

            with open(
                carpeta / "cheques_con_errores.csv",
                encoding="utf-8-sig",
                newline=""
            ) as archivo:
                lector = csv.DictReader(archivo)

                self.assertIn("estado", lector.fieldnames)
                self.assertIn("id_banco", lector.fieldnames)
                self.assertEqual(list(lector), [])


if __name__ == "__main__":
    unittest.main()