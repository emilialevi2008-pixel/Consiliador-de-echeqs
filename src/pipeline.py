from src.modelos import ChequeElectronico
from src.validaciones import convertir_fecha, convertir_importe


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