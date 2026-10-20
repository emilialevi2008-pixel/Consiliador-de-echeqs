import re
from src.pipeline import (
    COLUMNAS,
    preparar_filas,
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
def indexar_ids_rechazados(registro, origen):
    """Relaciona los IDs reconocibles rechazados con sus filas."""

    if origen not in COLUMNAS:
        raise ValueError("El origen debe ser banco o sistema.")

    nombre_columna = COLUMNAS[origen]["identificador"]
    rechazados_por_id = {}

    for entrada in registro:
        if entrada["origen"] != origen:
            continue

        if entrada["estado"] != "rechazada":
            continue

        valor = entrada["original"].get(nombre_columna)

        if not isinstance(valor, str):
            continue

        identificador = valor.strip()

        if not re.fullmatch(r"[A-Za-z0-9]+", identificador):
            continue

        if identificador not in rechazados_por_id:
            rechazados_por_id[identificador] = []

        rechazados_por_id[identificador].append(entrada["fila"])

    return rechazados_por_id
def candidatos_entre_ids(identificador, ids_banco):
    """Busca candidatos considerando también IDs de filas rechazadas."""

    if identificador in ids_banco:
        return [identificador]

    return [
        codigo for codigo in sorted(ids_banco)
        if len(codigo) > len(identificador)
        and codigo.startswith(identificador)
    ]


def conciliar_filas(filas_banco, filas_sistema):
    """Prepara y concilia las entradas, conservando todos los rechazos."""

    banco, registro_banco = preparar_filas(filas_banco, "banco")
    sistema, registro_sistema = preparar_filas(filas_sistema, "sistema")

    rechazados_banco = indexar_ids_rechazados(
        registro_banco, "banco"
    )
    rechazados_sistema = indexar_ids_rechazados(
        registro_sistema, "sistema"
    )

    duplicados_banco = detectar_duplicados(banco)
    duplicados_sistema = detectar_duplicados(sistema)

    ids_banco_validos = {
        registro["cheque"].identificador for registro in banco
    }
    ids_sistema_validos = {
        registro["cheque"].identificador for registro in sistema
    }

    todos_ids_banco = ids_banco_validos | set(rechazados_banco)
    todos_ids_sistema = ids_sistema_validos | set(rechazados_sistema)

    bloqueados_banco = {}
    bloqueados_sistema = {}

    # Una fila válida puede compartir ID con otra fila rechazada.
    for registro in banco:
        codigo = registro["cheque"].identificador

        if codigo in duplicados_banco or codigo in rechazados_banco:
            bloqueados_banco[registro["fila"]] = (
                "ID_DUPLICADO",
                "El ID aparece en varias filas bancarias."
            )
            continue
        tiene_exacto_valido = (
            codigo in ids_sistema_validos
            and codigo not in duplicados_sistema
            and codigo not in rechazados_sistema
        )

        ids_problematicos = set(rechazados_sistema) | set(duplicados_sistema)

        for codigo_problematico in ids_problematicos:
            candidatos = candidatos_entre_ids(
                codigo_problematico, todos_ids_banco
            )

            if codigo in candidatos and not tiene_exacto_valido:
                bloqueados_banco[registro["fila"]] = (
                    "PENDIENTE_REVISION",
                    "Una fila del sistema rechazada o duplicada "
                    "podría corresponder a este cheque."
                )
                break
        

    ids_banco_bloqueados = {
        registro["cheque"].identificador
        for registro in banco
        if registro["fila"] in bloqueados_banco
    }

    for registro in sistema:
        codigo = registro["cheque"].identificador

        if codigo in duplicados_sistema or codigo in rechazados_sistema:
            bloqueados_sistema[registro["fila"]] = (
                "ID_DUPLICADO",
                "El ID aparece en varias filas del sistema."
            )
            continue

        candidatos = candidatos_entre_ids(codigo, todos_ids_banco)

        hay_bloqueo = any(
            candidato in rechazados_banco
            or candidato in ids_banco_bloqueados
            for candidato in candidatos
        )

        if hay_bloqueo:
            if len(candidatos) > 1:
                estado = "COINCIDENCIA_AMBIGUA"
            else:
                estado = "PENDIENTE_REVISION"

            bloqueados_sistema[registro["fila"]] = (
                estado,
                "Hay candidatos bancarios con filas inválidas "
                "o bloqueadas: " + ", ".join(candidatos)
            )

    banco_disponible = [
        registro for registro in banco
        if registro["fila"] not in bloqueados_banco
    ]
    sistema_disponible = [
        registro for registro in sistema
        if registro["fila"] not in bloqueados_sistema
    ]

    resultados = conciliar_preparados(
        banco_disponible, sistema_disponible
    )

    # No informar ausencia si existe una contraparte sin resolver.
    for resultado in resultados:
        if resultado["estado"] != "NO_ESTA_EN_SISTEMA":
            continue

        codigo_banco = resultado["id_banco"]

        tiene_contraparte = any(
            codigo_banco in candidatos_entre_ids(codigo, todos_ids_banco)
            for codigo in todos_ids_sistema
        )

        if tiene_contraparte:
            resultado["estado"] = "PENDIENTE_REVISION"
            resultado["tipo_error"] = "PENDIENTE_REVISION"
            resultado["descripcion"] = (
                "Existe una posible contraparte que requiere revisión."
            )

    # Agregar cada fila bloqueada una sola vez.
    grupos = [
        ("banco", banco, bloqueados_banco),
        ("sistema", sistema, bloqueados_sistema)
    ]

    for origen, registros, bloqueados in grupos:
        for registro in registros:
            if registro["fila"] in bloqueados:
                estado, descripcion = bloqueados[registro["fila"]]

                resultados.append(
                    resultado_individual(
                        registro, origen, estado, descripcion
                    )
                )

    # Agregar todos los rechazos, incluso aquellos sin ID reconocible.
    grupos_rechazados = [
        ("banco", registro_banco, rechazados_banco, ids_banco_validos),
        ("sistema", registro_sistema, rechazados_sistema, ids_sistema_validos)
    ]

    for origen, registro, indice, ids_validos in grupos_rechazados:
        nombre_columna = COLUMNAS[origen]["identificador"]

        for entrada in registro:
            if entrada["estado"] != "rechazada":
                continue

            resultado = resultado_rechazado(entrada)
            codigo = entrada["original"].get(nombre_columna)

            if isinstance(codigo, str):
                codigo = codigo.strip()

                if codigo in indice:
                    if codigo in ids_validos or len(indice[codigo]) > 1:
                        resultado["tipo_error"] += "|ID_DUPLICADO"
                        resultado["descripcion"] += (
                            " Además, el ID está repetido en esta fuente."
                        )

            resultados.append(resultado)

    # Comprobar que ninguna fila se perdió ni se utilizó dos veces.
    for campo, cantidad in [
        ("fila_banco", len(filas_banco)),
        ("fila_sistema", len(filas_sistema))
    ]:
        numeros = [
            resultado[campo] for resultado in resultados
            if resultado[campo] != ""
        ]

        if sorted(numeros) != list(range(1, cantidad + 1)):
            raise ValueError(
                "No se conservó correctamente la procedencia de las filas."
            )

    auditoria = registro_banco + registro_sistema

    return resultados, auditoria