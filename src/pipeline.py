from src.modelos import ChequeElectronico
from src.validaciones import (
    convertir_fecha,
    convertir_importe,
    mostrar_fecha
)

COLUMNAS = {
    "banco": {
        "identificador": "ID Cheque",
        "importe": "Importe",
        "fecha_pago": "Fecha Pago"
    },
    "sistema": {
        "identificador": "ID CHEQUE",
        "importe": "IMPORTE",
        "fecha_pago": "FECHA DE COBRO"
    }
}


def convertir_fila(fila, origen):
    """Prepara un registro del banco o del sistema para compararlo."""

    if origen not in COLUMNAS:
        raise ValueError("El origen debe ser banco o sistema.")

    columnas = COLUMNAS[origen]

    for nombre_columna in columnas.values():
        if nombre_columna not in fila:
            raise ValueError(
                f"Falta la columna obligatoria: {nombre_columna}"
            )

    identificador = fila[columnas["identificador"]]
    importe = convertir_importe(fila[columnas["importe"]])
    fecha_pago = convertir_fecha(fila[columnas["fecha_pago"]])

    return ChequeElectronico(
        identificador,
        importe,
        fecha_pago
    )
def preparar_filas(filas, origen):
    """Prepara las filas y registra rechazos y modificaciones."""

    if origen not in COLUMNAS:
        raise ValueError("El origen debe ser banco o sistema.")

    preparados = []
    registro = []

    for numero, fila in enumerate(filas, start=1):
        original = fila.copy()

        try:
            cheque = convertir_fila(fila, origen)

        except ValueError as error:
            registro.append({
                "origen": origen,
                "fila": numero,
                "estado": "rechazada",
                "motivo": str(error),
                "original": original
            })
            continue

        preparados.append({
            "origen": origen,
            "fila": numero,
            "cheque": cheque,
            "original": original
        })

        columnas = COLUMNAS[origen]

        normalizados = {
            columnas["identificador"]: cheque.identificador,
            columnas["importe"]: format(cheque.importe, ".2f"),
            columnas["fecha_pago"]: mostrar_fecha(cheque.fecha_pago)
        }

        cambios = {}

        for columna, valor_nuevo in normalizados.items():
            valor_original = fila[columna]

            if valor_original != valor_nuevo:
                cambios[columna] = {
                    "antes": valor_original,
                    "despues": valor_nuevo
                }

        if cambios:
            registro.append({
                "origen": origen,
                "fila": numero,
                "estado": "modificada",
                "cambios": cambios,
                "original": original
            })

    return preparados, registro
def detectar_duplicados(registros):
    """Encuentra los identificadores que aparecen más de una vez."""

    filas_por_id = {}

    for registro in registros:
        identificador = registro["cheque"].identificador
        numero_fila = registro["fila"]

        if identificador not in filas_por_id:
            filas_por_id[identificador] = []

        filas_por_id[identificador].append(numero_fila)

    duplicados = {}

    for identificador, filas in filas_por_id.items():
        if len(filas) > 1:
            duplicados[identificador] = filas

    return duplicados