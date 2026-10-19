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
def buscar_candidatos(identificador_sistema, registros_banco):
    """Busca coincidencias exactas o por prefijo del ID del sistema."""

    if not isinstance(identificador_sistema, str):
        raise ValueError("El identificador debe ser texto.")

    if not identificador_sistema:
        raise ValueError("El identificador no puede estar vacío.")

    exactos = []

    for registro in registros_banco:
        identificador_banco = registro["cheque"].identificador

        if identificador_banco == identificador_sistema:
            exactos.append(registro)

    if exactos:
        return exactos

    candidatos = []

    for registro in registros_banco:
        identificador_banco = registro["cheque"].identificador

        if (
            len(identificador_sistema) < len(identificador_banco)
            and identificador_banco.startswith(identificador_sistema)
        ):
            candidatos.append(registro)

    return candidatos
def comparar_registros(registro_banco, registro_sistema):
    """Compara un par de registros relacionados por su identificador."""

    banco = registro_banco["cheque"]
    sistema = registro_sistema["cheque"]

    if not banco.identificador.startswith(sistema.identificador):
        raise ValueError("Los identificadores no corresponden.")

    errores = banco.diferencias(sistema)
    descripciones = []

    if "ERROR_IMPORTE" in errores:
        descripciones.append(
            f"Importes diferentes: banco {banco.importe:.2f}; "
            f"sistema {sistema.importe:.2f}."
        )

    if "ERROR_FECHA" in errores:
        descripciones.append(
            f"Fechas diferentes: banco {mostrar_fecha(banco.fecha_pago)}; "
            f"sistema {mostrar_fecha(sistema.fecha_pago)}."
        )

    if len(errores) == 2:
        estado = "CON_DIFERENCIAS"
    elif len(errores) == 1:
        estado = errores[0]
    elif banco.identificador == sistema.identificador:
        estado = "CONCILIADO"
    else:
        estado = "CONCILIADO_ID_ABREVIADO"

    if not errores:
        descripciones.append("Coinciden el importe y la fecha de pago.")

    return {
        "id_banco": banco.identificador,
        "id_sistema": sistema.identificador,
        "importe_banco": format(banco.importe, ".2f"),
        "importe_sistema": format(sistema.importe, ".2f"),
        "diferencia_importe": format(
            banco.diferencia_importe(sistema), ".2f"
        ),
        "fecha_banco": mostrar_fecha(banco.fecha_pago),
        "fecha_sistema": mostrar_fecha(sistema.fecha_pago),
        "estado": estado,
        "tipo_error": "|".join(errores),
        "descripcion": " ".join(descripciones),
        "fila_banco": registro_banco["fila"],
        "fila_sistema": registro_sistema["fila"]
    }