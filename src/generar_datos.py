import csv
import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


def generar_datos(carpeta="data/ejemplos"):
    """Genera datos ficticios reproducibles para probar el programa."""

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    banco = []
    sistema = []

    inicio = date(2026, 10, 18)

    for numero in range(1, 101):
        identificador = f"CH{numero:04d}XYZ"
        fecha_pago = inicio + timedelta(days=numero)
        importe = Decimal("1000.00") + Decimal(numero) * Decimal("25.50")

        fila_banco = {
            "ID Cheque": identificador,
            "Nombre o Razón Social Emisor": (
                f"Empresa ficticia {numero:03d}"
            ),
            "Historial de Endosos": "Sin endosos",
            "Fecha Emisión": inicio.strftime("%d/%m/%Y"),
            "Fecha Pago": fecha_pago.strftime("%d/%m/%Y"),
            "Importe": format(importe, ".2f")
        }

        fila_sistema = {
            "ID CHEQUE": identificador,
            "FECHA DE EMISION": inicio.strftime("%d/%m/%Y"),
            "FECHA DE COBRO": fecha_pago.strftime("%d/%m/%Y"),
            "BANCO": "Banco ficticio",
            "TITULAR": f"Empresa ficticia {numero:03d}",
            "IMPORTE": format(importe, ".2f")
        }

        # Algunos identificadores del sistema están abreviados.
        if numero % 4 == 0:
            fila_sistema["ID CHEQUE"] = f"CH{numero:04d}"

        # Diferencia de importe.
        if numero == 3:
            fila_sistema["IMPORTE"] = format(
                importe + Decimal("10.00"), ".2f"
            )

        # Diferencia de fecha.
        if numero == 5:
            fila_sistema["FECHA DE COBRO"] = (
                fecha_pago + timedelta(days=1)
            ).strftime("%d/%m/%Y")

        # Diferencias de importe y fecha.
        if numero == 6:
            fila_sistema["IMPORTE"] = format(
                importe + Decimal("20.00"), ".2f"
            )
            fila_sistema["FECHA DE COBRO"] = (
                fecha_pago + timedelta(days=2)
            ).strftime("%d/%m/%Y")

        # Un registro del sistema sin contraparte bancaria.
        if numero == 8:
            fila_sistema["ID CHEQUE"] = "EXTRA0008"

        # Datos bancarios inválidos.
        if numero == 9:
            fila_banco["Importe"] = "abc"

        if numero == 10:
            fila_banco["Fecha Pago"] = "31/02/2026"

        if numero == 11:
            fila_banco["ID Cheque"] = "???"

        banco.append(fila_banco)

        # El cheque 7 aparece únicamente en el banco.
        if numero != 7:
            sistema.append(fila_sistema)

        # Duplicados intencionales para comprobar su detección.
        if numero == 12:
            banco.append(fila_banco.copy())

        if numero == 13:
            sistema.append(fila_sistema.copy())

    with open(
        carpeta / "banco.csv",
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=list(banco[0])
        )
        escritor.writeheader()
        escritor.writerows(banco)

    with open(
        carpeta / "sistema.json",
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            sistema,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    print(f"Archivo bancario: {len(banco)} registros.")
    print(f"Archivo del sistema: {len(sistema)} registros.")
    print(f"Ejemplos guardados en: {carpeta.resolve()}")


if __name__ == "__main__":
    generar_datos()