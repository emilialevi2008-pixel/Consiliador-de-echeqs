import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.generar_datos import generar_datos
from src.main import cargar_archivo, ejecutar_comparacion


class TestProgramaCompleto(unittest.TestCase):

    def test_comparar_archivos_y_generar_reportes(self):
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            datos = carpeta / "datos"
            salida = carpeta / "resultados"

            generar_datos(datos)

            resultados, importes = ejecutar_comparacion(
                datos / "banco.csv",
                datos / "sistema.json",
                salida
            )

            conciliados = [
                resultado
                for resultado in resultados
                if resultado["estado"] in (
                    "CONCILIADO",
                    "CONCILIADO_ID_ABREVIADO"
                )
            ]

            self.assertEqual(len(conciliados), 90)
            self.assertEqual(
                importes["total_banco"],
                Decimal("228851.50")
            )
            self.assertEqual(
                importes["total_sistema"],
                Decimal("228958.00")
            )
            self.assertEqual(
                importes["diferencia"],
                Decimal("-106.50")
            )

            filas_banco = [
                resultado["fila_banco"]
                for resultado in resultados
                if resultado["fila_banco"] != ""
            ]

            filas_sistema = [
                resultado["fila_sistema"]
                for resultado in resultados
                if resultado["fila_sistema"] != ""
            ]

            self.assertEqual(
                sorted(filas_banco),
                list(range(1, 102))
            )
            self.assertEqual(
                sorted(filas_sistema),
                list(range(1, 101))
            )

            with open(
                salida / "resumen.json",
                encoding="utf-8"
            ) as archivo:
                resumen = json.load(archivo)

            self.assertEqual(
                resumen["importes"]["diferencia"],
                "-106.50"
            )
            self.assertTrue(
                (salida / "reporte_conciliacion.csv").is_file()
            )
            self.assertTrue(
                (salida / "cheques_con_errores.csv").is_file()
            )
            self.assertTrue(
                (salida / "resumen_importes.csv").is_file()
            )

    def test_archivo_inexistente_no_se_oculta(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "no_existe.csv"

            with self.assertRaises(FileNotFoundError):
                cargar_archivo(ruta)


if __name__ == "__main__":
    unittest.main()