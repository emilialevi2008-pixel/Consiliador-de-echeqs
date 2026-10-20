import argparse
from pathlib import Path
from zipfile import BadZipFile

from openpyxl.utils.exceptions import InvalidFileException

from src.conciliacion import conciliar_filas
from src.fuentes import FuenteCSV, FuenteJSON, FuenteExcel
from src.importes import resumir_importes
from src.reportes import generar_reportes


def cargar_archivo(ruta):
    """Selecciona el lector según la extensión del archivo."""

    extension = Path(ruta).suffix.lower()

    fuentes = {
        ".csv": FuenteCSV,
        ".json": FuenteJSON,
        ".xlsx": FuenteExcel
    }

    if extension not in fuentes:
        raise ValueError(
            "Formato no admitido. Usar CSV, JSON o Excel .xlsx."
        )

    fuente = fuentes[extension]()
    return fuente.cargar(ruta)


def ejecutar_comparacion(ruta_banco, ruta_sistema, carpeta_salida):
    """Carga los datos, los compara y guarda los resultados."""

    filas_banco = cargar_archivo(ruta_banco)
    filas_sistema = cargar_archivo(ruta_sistema)

    resultados, auditoria = conciliar_filas(
        filas_banco,
        filas_sistema
    )

    importes = resumir_importes(
        filas_banco,
        filas_sistema,
        resultados
    )

    generar_reportes(
        carpeta_salida,
        resultados,
        auditoria,
        importes
    )

    return resultados, importes


def main():
    argumentos = argparse.ArgumentParser(
        description="Comparar cheques del banco y del sistema."
    )

    argumentos.add_argument(
        "--banco",
        required=True,
        help="Ruta del archivo bancario."
    )

    argumentos.add_argument(
        "--sistema",
        required=True,
        help="Ruta del archivo del sistema."
    )

    argumentos.add_argument(
        "--salida",
        default="outputs",
        help="Carpeta para guardar los reportes."
    )

    opciones = argumentos.parse_args()

    try:
        resultados, importes = ejecutar_comparacion(
            opciones.banco,
            opciones.sistema,
            opciones.salida
        )

    except (
        OSError,
        ValueError,
        BadZipFile,
        InvalidFileException
    ) as error:
        print(f"No se pudo completar la comparación: {error}")
        return 1

    conciliados = sum(
        resultado["estado"] in (
            "CONCILIADO",
            "CONCILIADO_ID_ABREVIADO"
        )
        for resultado in resultados
    )

    print("Comparación terminada.")
    print(f"Pares conciliados: {conciliados}")
    print(
        "Resultados que requieren revisión: "
        f"{len(resultados) - conciliados}"
    )
    print(f"Total bruto del banco: {importes['total_banco']:.2f}")
    print(f"Total bruto del sistema: {importes['total_sistema']:.2f}")
    print(
        "Diferencia, banco menos sistema: "
        f"{importes['diferencia']:.2f}"
    )
    print("Una diferencia global de cero no garantiza la conciliación.")
    print(f"Reportes guardados en: {Path(opciones.salida).resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())