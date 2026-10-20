import csv
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.conciliacion import conciliar_filas
from src.main import ejecutar_comparacion


class TestEscenariosConciliacion(unittest.TestCase):
    """Seis escenarios con datos ficticios y resultados conocidos."""

    def setUp(self):
        """Prepara tres pares válidos antes de cada prueba."""
        self.banco = [
            {
                "ID Cheque": "ABC123",
                "Fecha Pago": "19/10/2026",
                "Importe": "100.00"
            },
            {
                "ID Cheque": "DEF456",
                "Fecha Pago": "20/10/2026",
                "Importe": "200.00"
            },
            {
                "ID Cheque": "MKX9R4GYWZK9O6W",
                "Fecha Pago": "21/10/2026",
                "Importe": "300.50"
            }
        ]

        self.sistema = [
            {
                "ID CHEQUE": "ABC123",
                "FECHA DE COBRO": "19/10/2026",
                "IMPORTE": "100.00"
            },
            {
                "ID CHEQUE": "DEF456",
                "FECHA DE COBRO": "20/10/2026",
                "IMPORTE": "200.00"
            },
            {
                "ID CHEQUE": "MKX9R4GY",
                "FECHA DE COBRO": "21/10/2026",
                "IMPORTE": "300.50"
            }
        ]

    def test_todos_los_cheques_conciliados(self):
        """Los archivos coincidentes producen tres pares sin errores."""
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            ruta_banco = carpeta / "banco.csv"
            ruta_sistema = carpeta / "sistema.json"
            salida = carpeta / "reportes"

            with open(
                ruta_banco, "w", encoding="utf-8", newline=""
            ) as archivo:
                escritor = csv.DictWriter(
                    archivo,
                    fieldnames=self.banco[0].keys()
                )
                escritor.writeheader()
                escritor.writerows(self.banco)

            with open(
                ruta_sistema, "w", encoding="utf-8"
            ) as archivo:
                json.dump(self.sistema, archivo)

            resultados, importes = ejecutar_comparacion(
                ruta_banco, ruta_sistema, salida
            )

            self.assertEqual(len(resultados), 3)

            por_id = {
                fila["id_banco"]: fila
                for fila in resultados
            }

            self.assertEqual(
                por_id["ABC123"]["estado"], "CONCILIADO"
            )
            self.assertEqual(
                por_id["DEF456"]["estado"], "CONCILIADO"
            )
            self.assertEqual(
                por_id["MKX9R4GYWZK9O6W"]["estado"],
                "CONCILIADO_ID_ABREVIADO"
            )

            # Ninguna fila debe perderse ni utilizarse dos veces.
            self.assertEqual(
                sorted(f["fila_banco"] for f in resultados),
                [1, 2, 3]
            )
            self.assertEqual(
                sorted(f["fila_sistema"] for f in resultados),
                [1, 2, 3]
            )

            self.assertEqual(
                importes["total_banco"], Decimal("600.50")
            )
            self.assertEqual(
                importes["total_sistema"], Decimal("600.50")
            )
            self.assertEqual(
                importes["importe_conciliado"], Decimal("600.50")
            )
            self.assertEqual(
                importes["diferencia"], Decimal("0.00")
            )

            with open(
                salida / "cheques_con_errores.csv",
                encoding="utf-8-sig",
                newline=""
            ) as archivo:
                lector = csv.DictReader(archivo)
                self.assertIn("estado", lector.fieldnames)
                self.assertEqual(list(lector), [])

    def test_ningun_cheque_conciliado(self):
        """Todos los pares difieren en fecha e importe."""
        for fila in self.sistema:
            fila["FECHA DE COBRO"] = "01/11/2026"
            fila["IMPORTE"] = "50.00"

        resultados, _ = conciliar_filas(
            self.banco, self.sistema
        )

        self.assertEqual(len(resultados), 3)
        self.assertEqual(
            [fila["estado"] for fila in resultados],
            ["CON_DIFERENCIAS"] * 3
        )

        for fila in resultados:
            self.assertEqual(
                fila["tipo_error"],
                "ERROR_IMPORTE|ERROR_FECHA"
            )

    def test_error_de_fecha(self):
        """Una fecha distinta afecta solo al cheque correspondiente."""
        self.sistema[0]["FECHA DE COBRO"] = "22/10/2026"

        resultados, _ = conciliar_filas(
            self.banco, self.sistema
        )
        por_id = {
            fila["id_banco"]: fila
            for fila in resultados
        }

        self.assertEqual(len(resultados), 3)
        self.assertEqual(
            por_id["ABC123"]["estado"], "ERROR_FECHA"
        )
        self.assertEqual(
            por_id["ABC123"]["tipo_error"], "ERROR_FECHA"
        )
        self.assertEqual(
            por_id["ABC123"]["fecha_banco"], "19/10/2026"
        )
        self.assertEqual(
            por_id["ABC123"]["fecha_sistema"], "22/10/2026"
        )
        self.assertEqual(
            por_id["ABC123"]["diferencia_importe"], "0.00"
        )
        self.assertEqual(
            por_id["DEF456"]["estado"], "CONCILIADO"
        )
        self.assertEqual(
            por_id["MKX9R4GYWZK9O6W"]["estado"],
            "CONCILIADO_ID_ABREVIADO"
        )

    def test_error_de_id(self):
        """IDs sin relación no se emparejan por fecha e importe."""
        self.sistema[0]["ID CHEQUE"] = "XYZ999"

        resultados, _ = conciliar_filas(
            self.banco, self.sistema
        )
        estados = [
            fila["estado"] for fila in resultados
        ]

        # El par sin correspondencia genera dos registros individuales.
        self.assertEqual(len(resultados), 4)
        self.assertCountEqual(
            estados,
            [
                "CONCILIADO",
                "CONCILIADO_ID_ABREVIADO",
                "NO_ESTA_EN_BANCO",
                "NO_ESTA_EN_SISTEMA"
            ]
        )

        sin_banco = next(
            f for f in resultados
            if f["estado"] == "NO_ESTA_EN_BANCO"
        )
        sin_sistema = next(
            f for f in resultados
            if f["estado"] == "NO_ESTA_EN_SISTEMA"
        )

        self.assertEqual(
            sin_banco["id_sistema"], "XYZ999"
        )
        self.assertEqual(
            sin_banco["fila_sistema"], 1
        )
        self.assertEqual(
            sin_banco["id_banco"], ""
        )
        self.assertEqual(
            sin_sistema["id_banco"], "ABC123"
        )
        self.assertEqual(
            sin_sistema["fila_banco"], 1
        )
        self.assertEqual(
            sin_sistema["id_sistema"], ""
        )

    def test_error_de_importe(self):
        """Se detecta el importe distinto y se calcula la diferencia."""
        self.sistema[0]["IMPORTE"] = "90.00"

        resultados, _ = conciliar_filas(
            self.banco, self.sistema
        )
        por_id = {
            fila["id_banco"]: fila
            for fila in resultados
        }

        self.assertEqual(len(resultados), 3)
        self.assertEqual(
            por_id["ABC123"]["estado"], "ERROR_IMPORTE"
        )
        self.assertEqual(
            por_id["ABC123"]["tipo_error"], "ERROR_IMPORTE"
        )
        self.assertEqual(
            por_id["ABC123"]["importe_banco"], "100.00"
        )
        self.assertEqual(
            por_id["ABC123"]["importe_sistema"], "90.00"
        )
        self.assertEqual(
            por_id["ABC123"]["diferencia_importe"], "10.00"
        )
        self.assertEqual(
            por_id["DEF456"]["estado"], "CONCILIADO"
        )
        self.assertEqual(
            por_id["MKX9R4GYWZK9O6W"]["estado"],
            "CONCILIADO_ID_ABREVIADO"
        )

    def test_fecha_invalida_se_registra_para_revision(self):
        """Una fecha imposible se rechaza conservando fila y motivo."""
        self.sistema[0]["FECHA DE COBRO"] = "31/02/2026"

        resultados, auditoria = conciliar_filas(
            self.banco, self.sistema
        )
        estados = [
            fila["estado"] for fila in resultados
        ]

        self.assertEqual(len(resultados), 4)
        self.assertCountEqual(
            estados,
            [
                "CONCILIADO",
                "CONCILIADO_ID_ABREVIADO",
                "DATOS_INVALIDOS",
                "PENDIENTE_REVISION"
            ]
        )

        rechazos = [
            fila for fila in auditoria
            if fila["estado"] == "rechazada"
        ]

        self.assertEqual(len(rechazos), 1)
        self.assertEqual(
            rechazos[0]["origen"], "sistema"
        )
        self.assertEqual(
            rechazos[0]["fila"], 1
        )
        self.assertEqual(
            rechazos[0]["original"]["FECHA DE COBRO"],
            "31/02/2026"
        )
        self.assertTrue(rechazos[0]["motivo"])

        invalido = next(
            f for f in resultados
            if f["estado"] == "DATOS_INVALIDOS"
        )
        pendiente = next(
            f for f in resultados
            if f["estado"] == "PENDIENTE_REVISION"
        )

        self.assertEqual(
            invalido["id_sistema"], "ABC123"
        )
        self.assertEqual(
            pendiente["id_banco"], "ABC123"
        )


if __name__ == "__main__":
    unittest.main()