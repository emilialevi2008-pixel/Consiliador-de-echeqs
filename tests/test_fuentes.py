import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.fuentes import FuenteCSV, FuenteJSON


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


if __name__ == "__main__":
    unittest.main()