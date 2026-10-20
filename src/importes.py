import re
from decimal import Decimal

from src.pipeline import COLUMNAS
from src.validaciones import convertir_importe


def calcular_total_archivo(filas, origen):
    """Suma los importes válidos y documenta las exclusiones."""

    if origen not in COLUMNAS:
        raise ValueError("El origen debe ser banco o sistema.")

    columnas = COLUMNAS[origen]
    total = Decimal("0.00")

    filas_incluidas = []
    detalle_excluidos = []
    ids_por_fila = {}
    cantidad_por_id = {}

    for numero, fila in enumerate(filas, start=1):
        identificador = fila.get(columnas["identificador"])

        if isinstance(identificador, str):
            identificador = identificador.strip()

            if re.fullmatch(r"[A-Za-z0-9]+", identificador):
                ids_por_fila[numero] = identificador

                if identificador not in cantidad_por_id:
                    cantidad_por_id[identificador] = 0

                cantidad_por_id[identificador] += 1

        valor_original = fila.get(columnas["importe"])

        try:
            importe = convertir_importe(valor_original)

        except ValueError as error:
            detalle_excluidos.append({
                "origen": origen,
                "fila": numero,
                "identificador": fila.get(
                    columnas["identificador"]
                ),
                "importe_original": valor_original,
                "motivo": str(error)
            })
            continue

        total += importe
        filas_incluidas.append(numero)

    duplicados_incluidos = []

    for numero in filas_incluidas:
        identificador = ids_por_fila.get(numero)

        if identificador is not None:
            if cantidad_por_id[identificador] > 1:
                duplicados_incluidos.append(numero)

    return {
        "total": total,
        "incluidos": len(filas_incluidas),
        "excluidos": len(detalle_excluidos),
        "filas_incluidas": filas_incluidas,
        "detalle_excluidos": detalle_excluidos,
        "duplicados_incluidos": duplicados_incluidos
    }
def resumir_importes(filas_banco, filas_sistema, resultados):
    """Calcula totales brutos, conciliados y de pares con diferencias."""

    banco = calcular_total_archivo(filas_banco, "banco")
    sistema = calcular_total_archivo(filas_sistema, "sistema")

    importe_conciliado = Decimal("0.00")
    diferencias_banco = Decimal("0.00")
    diferencias_sistema = Decimal("0.00")

    filas_utilizadas = {
        "banco": set(),
        "sistema": set()
    }

    estados_conciliados = (
        "CONCILIADO",
        "CONCILIADO_ID_ABREVIADO"
    )

    estados_con_diferencias = (
        "ERROR_IMPORTE",
        "ERROR_FECHA",
        "CON_DIFERENCIAS"
    )

    for resultado in resultados:
        for origen in ("banco", "sistema"):
            numero = resultado[f"fila_{origen}"]

            if numero == "":
                continue

            if numero in filas_utilizadas[origen]:
                raise ValueError(
                    f"La fila {numero} de {origen} aparece más de una vez."
                )

            filas_utilizadas[origen].add(numero)

        estado = resultado["estado"]

        if (
            estado not in estados_conciliados
            and estado not in estados_con_diferencias
        ):
            continue

        importe_banco = convertir_importe(
            resultado["importe_banco"]
        )
        importe_sistema = convertir_importe(
            resultado["importe_sistema"]
        )

        if estado in estados_conciliados:
            if importe_banco != importe_sistema:
                raise ValueError(
                    "Un par marcado como conciliado tiene importes distintos."
                )

            importe_conciliado += importe_banco

        else:
            diferencias_banco += importe_banco
            diferencias_sistema += importe_sistema

    for origen, filas in [
        ("banco", filas_banco),
        ("sistema", filas_sistema)
    ]:
        esperadas = set(range(1, len(filas) + 1))

        if filas_utilizadas[origen] != esperadas:
            raise ValueError(
                f"Los resultados no incluyen todas las filas de {origen}."
            )

    diferencia = banco["total"] - sistema["total"]

    return {
        "total_banco": banco["total"],
        "total_sistema": sistema["total"],
        "diferencia": diferencia,
        "diferencia_absoluta": abs(diferencia),
        "importe_conciliado": importe_conciliado,
        "importe_con_diferencias_banco": diferencias_banco,
        "importe_con_diferencias_sistema": diferencias_sistema,
        "detalle_banco": banco,
        "detalle_sistema": sistema
    }