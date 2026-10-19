from datetime import date, datetime
import re
from decimal import Decimal, InvalidOperation


def convertir_fecha(valor):
    """Convierte una fecha de entrada en una fecha de Python."""

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    if not isinstance(valor, str):
        raise ValueError("La fecha no tiene un formato reconocido.")

    texto = valor.strip()

    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue

    raise ValueError(
        "Fecha inválida. Usar DD/MM/AAAA o AAAA-MM-DD."
    )


def mostrar_fecha(fecha):
    """Muestra una fecha en el formato usado en Argentina."""

    return fecha.strftime("%d/%m/%Y")

def convertir_importe(valor):
    """Convierte un importe a Decimal y comprueba que sea válido."""

    if valor is None:
        raise ValueError("El importe está vacío.")

    texto = str(valor).strip().replace(",", ".")

    if not re.fullmatch(r"[+-]?[0-9]+(?:\.[0-9]{1,2})?", texto):
        raise ValueError(
            "Importe inválido. Usar hasta dos decimales y sin miles."
        )

    try:
        importe = Decimal(texto)

        if importe < 0:
            raise ValueError("El importe no puede ser negativo.")

        return importe.quantize(Decimal("0.01"))

    except InvalidOperation:
        raise ValueError("El importe no se puede convertir.")