from datetime import date, datetime


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