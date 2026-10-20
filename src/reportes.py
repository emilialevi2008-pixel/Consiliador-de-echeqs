import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path


COLUMNAS_REPORTE = [
    "id_banco",
    "id_sistema",
    "importe_banco",
    "importe_sistema",
    "diferencia_importe",
    "fecha_banco",
    "fecha_sistema",
    "estado",
    "tipo_error",
    "descripcion",
    "fila_banco",
    "fila_sistema"
]


def escribir_csv(ruta, columnas, filas):
    """Guarda un CSV con encabezados, aunque no haya resultados."""

    with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas
        )
        escritor.writeheader()
        escritor.writerows(filas)


def convertir_para_json(valor):
    """Permite guardar importes exactos y fechas dentro del JSON."""

    if isinstance(valor, Decimal):
        return format(valor, ".2f")

    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")

    raise TypeError(
        f"No se puede guardar un valor de tipo {type(valor).__name__}."
    )


def generar_reportes(carpeta, resultados, auditoria, resumen_importes):
    """Genera los reportes de una comparación."""

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    estados_conciliados = (
        "CONCILIADO",
        "CONCILIADO_ID_ABREVIADO"
    )

    errores = [
        resultado
        for resultado in resultados
        if resultado["estado"] not in estados_conciliados
    ]

    escribir_csv(
        carpeta / "reporte_conciliacion.csv",
        COLUMNAS_REPORTE,
        resultados
    )

    escribir_csv(
        carpeta / "cheques_con_errores.csv",
        COLUMNAS_REPORTE,
        errores
    )

    cantidades_por_estado = {}

    for resultado in resultados:
        estado = resultado["estado"]

        if estado not in cantidades_por_estado:
            cantidades_por_estado[estado] = 0

        cantidades_por_estado[estado] += 1

    resumen = {
        "cantidad_resultados": len(resultados),
        "cantidades_por_estado": cantidades_por_estado,
        "importes": resumen_importes,
        "auditoria": auditoria,
        "interpretacion": (
            "La diferencia de importes se calcula como banco menos sistema. "
            "Los totales brutos incluyen importes válidos de filas duplicadas. "
            "Una diferencia global de cero no garantiza la conciliación."
        )
    }

    with open(
        carpeta / "resumen.json",
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            resumen,
            archivo,
            ensure_ascii=False,
            indent=4,
            default=convertir_para_json
        )

    conceptos = [
        ("Total bruto del banco", "total_banco"),
        ("Total bruto del sistema", "total_sistema"),
        ("Diferencia: banco menos sistema", "diferencia"),
        ("Diferencia absoluta", "diferencia_absoluta"),
        ("Importe conciliado", "importe_conciliado"),
        (
            "Importe bancario de pares con diferencias",
            "importe_con_diferencias_banco"
        ),
        (
            "Importe del sistema de pares con diferencias",
            "importe_con_diferencias_sistema"
        )
    ]

    filas_importes = []

    for concepto, clave in conceptos:
        filas_importes.append({
            "concepto": concepto,
            "importe": format(resumen_importes[clave], ".2f")
        })

    escribir_csv(
        carpeta / "resumen_importes.csv",
        ["concepto", "importe"],
        filas_importes
    )