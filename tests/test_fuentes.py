from openpyxl import Workbook
import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.fuentes import FuenteCSV, FuenteJSON, FuenteExcel


class TestFuentes(unittest.TestCase):

    def test_csv_y_json_equivalentes(self):
        datos = [
            {
                "ID CHEQUE": "MKX9R4GY",
                "FECHA DE COBRO": "19/10/2026",
                "IMPORTE": "15000.50",
            }
        ]

        with tempfile.TemporaryDirectory() as carpeta:
            ruta_csv = Path(carpeta) / "prueba.csv"
            ruta_json = Path(carpeta) / "prueba.json"

            with open(
                ruta_csv, "w", encoding="utf-8", newline=""
            ) as archivo:
                escritor = csv.DictWriter(
                    archivo, fieldnames=datos[0].keys()
                )
                escritor.writeheader()
                escritor.writerows(datos)

            with open(ruta_json, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo)

            resultado_csv = FuenteCSV().cargar(ruta_csv)
            resultado_json = FuenteJSON().cargar(ruta_json)

            self.assertEqual(resultado_csv, datos)
            self.assertEqual(resultado_json, datos)


    def test_json_con_estructura_incorrecta(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_json = Path(carpeta) / "incorrecto.json"

            with open(ruta_json, "w", encoding="utf-8") as archivo:
                json.dump({"mensaje": "Esto no es una lista"}, archivo)

            with self.assertRaises(ValueError):
                FuenteJSON().cargar(ruta_json)

    def test_lectura_excel(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_excel = Path(carpeta) / "prueba.xlsx"

            libro = Workbook()
            hoja = libro.active

            hoja.append([
                "ID CHEQUE",
                "FECHA DE COBRO",
                "IMPORTE"
            ])

            hoja.append([
                "MKX9R4GY",
                "19/10/2026",
                15000.50
            ])

            libro.save(ruta_excel)
            libro.close()

            datos = FuenteExcel().cargar(ruta_excel)

            self.assertEqual(len(datos), 1)
            self.assertEqual(datos[0]["ID CHEQUE"], "MKX9R4GY")
            self.assertEqual(
                datos[0]["FECHA DE COBRO"],
                "19/10/2026"
            )
            self.assertEqual(datos[0]["IMPORTE"], 15000.50)
if __name__ == "__main__":
    unittest.main()