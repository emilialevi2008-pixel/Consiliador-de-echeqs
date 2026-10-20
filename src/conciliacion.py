from src.pipeline import (
    COLUMNAS,
    detectar_duplicados,
    buscar_candidatos,
    comparar_registros
)
from src.validaciones import mostrar_fecha


def resultado_individual(registro, origen, estado, descripcion):
    """Genera el resultado de una fila que no se pudo emparejar."""

    cheque = registro["cheque"]

    resultado = {
        "id_banco": "",
        "id_sistema": "",
        "importe_banco": "",
        "importe_sistema": "",
        "diferencia_importe": "",
        "fecha_banco": "",
        "fecha_sistema": "",
        "estado": estado,
        "tipo_error": estado,
        "descripcion": descripcion,
        "fila_banco": "",
        "fila_sistema": ""
    }

    resultado[f"id_{origen}"] = cheque.identificador
    resultado[f"importe_{origen}"] = format(cheque.importe, ".2f")
    resultado[f"fecha_{origen}"] = mostrar_fecha(cheque.fecha_pago)
    resultado[f"fila_{origen}"] = registro["fila"]

    return resultado


def conciliar_preparados(banco, sistema):
    """Concilia registros preparados sin reutilizar filas bancarias."""

    resultados = []
    filas_banco_resueltas = set()
    filas_banco_referenciadas = set()

    duplicados_banco = detectar_duplicados(banco)
    duplicados_sistema = detectar_duplicados(sistema)

    # Registrar todas las ocurrencias duplicadas del banco.
    for registro in banco:
        identificador = registro["cheque"].identificador

        if identificador in duplicados_banco:
            resultados.append(
                resultado_individual(
                    registro,
                    "banco",
                    "ID_DUPLICADO",
                    "El identificador aparece repetido en el banco."
                )
            )
            filas_banco_resueltas.add(registro["fila"])

    exactos = []
    abreviados = []

    for registro in sistema:
        identificador = registro["cheque"].identificador
        candidatos = buscar_candidatos(identificador, banco)

        for candidato in candidatos:
            filas_banco_referenciadas.add(candidato["fila"])

        if identificador in duplicados_sistema:
            resultados.append(
                resultado_individual(
                    registro,
                    "sistema",
                    "ID_DUPLICADO",
                    "El identificador aparece repetido en el sistema."
                )
            )
            continue

        if not candidatos:
            resultados.append(
                resultado_individual(
                    registro,
                    "sistema",
                    "NO_ESTA_EN_BANCO",
                    "No se encontró una correspondencia en el banco."
                )
            )
            continue

        if len(candidatos) > 1:
            codigos = [
                candidato["cheque"].identificador
                for candidato in candidatos
            ]

            resultados.append(
                resultado_individual(
                    registro,
                    "sistema",
                    "COINCIDENCIA_AMBIGUA",
                    "Hay varias filas bancarias candidatas: "
                    + ", ".join(codigos)
                )
            )
            continue

        candidato = candidatos[0]

        if candidato["cheque"].identificador == identificador:
            exactos.append((candidato, registro))
        else:
            abreviados.append((candidato, registro))

    # Resolver los IDs exactos antes de utilizar abreviaciones.
    for registro_banco, registro_sistema in exactos:
        resultados.append(
            comparar_registros(registro_banco, registro_sistema)
        )
        filas_banco_resueltas.add(registro_banco["fila"])

    propuestas = {}

    for registro_banco, registro_sistema in abreviados:
        numero = registro_banco["fila"]

        if numero in filas_banco_resueltas:
            resultados.append(
                resultado_individual(
                    registro_sistema,
                    "sistema",
                    "PENDIENTE_REVISION",
                    "El candidato bancario ya tiene una coincidencia exacta."
                )
            )
            continue

        if numero not in propuestas:
            propuestas[numero] = []

        propuestas[numero].append(
            (registro_banco, registro_sistema)
        )

    # No elegir por orden cuando varios prefijos compiten por un banco.
    for pares in propuestas.values():
        if len(pares) == 1:
            registro_banco, registro_sistema = pares[0]

            resultados.append(
                comparar_registros(registro_banco, registro_sistema)
            )
            filas_banco_resueltas.add(registro_banco["fila"])

        else:
            for registro_banco, registro_sistema in pares:
                resultados.append(
                    resultado_individual(
                        registro_sistema,
                        "sistema",
                        "COINCIDENCIA_AMBIGUA",
                        "Varios registros del sistema apuntan "
                        "a la misma fila bancaria."
                    )
                )

    # Informar también las filas bancarias que quedaron sin pareja.
    for registro in banco:
        numero = registro["fila"]

        if numero in filas_banco_resueltas:
            continue

        if numero in filas_banco_referenciadas:
            estado = "PENDIENTE_REVISION"
            descripcion = (
                "Existe una posible correspondencia, "
                "pero no pudo resolverse de forma segura."
            )
        else:
            estado = "NO_ESTA_EN_SISTEMA"
            descripcion = (
                "No se encontró una correspondencia en el sistema."
            )

        resultados.append(
            resultado_individual(
                registro,
                "banco",
                estado,
                descripcion
            )
        )

    return resultados
def resultado_rechazado(entrada):
    """Conserva una fila rechazada y explica por qué no pudo procesarse."""

    origen = entrada["origen"]
    original = entrada["original"]
    columnas = COLUMNAS[origen]

    resultado = {
        "id_banco": "",
        "id_sistema": "",
        "importe_banco": "",
        "importe_sistema": "",
        "diferencia_importe": "",
        "fecha_banco": "",
        "fecha_sistema": "",
        "estado": "DATOS_INVALIDOS",
        "tipo_error": "DATOS_INVALIDOS",
        "descripcion": entrada["motivo"],
        "fila_banco": "",
        "fila_sistema": ""
    }

    campos = {
        "identificador": f"id_{origen}",
        "importe": f"importe_{origen}",
        "fecha_pago": f"fecha_{origen}"
    }

    for campo, columna_resultado in campos.items():
        nombre_original = columnas[campo]
        valor = original.get(nombre_original)

        if valor is not None:
            resultado[columna_resultado] = str(valor)

    resultado[f"fila_{origen}"] = entrada["fila"]

    return resultado