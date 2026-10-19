import re
from datetime import date
from decimal import Decimal


class ChequeElectronico:
    """Representa los datos de un cheque para la conciliación."""

    def __init__(self, identificador, importe, fecha_pago):
        if not isinstance(identificador, str):
            raise ValueError("El identificador debe ser texto.")

        identificador = identificador.strip()

        if not re.fullmatch(r"[A-Za-z0-9]+", identificador):
            raise ValueError(
                "El identificador debe contener letras o números."
            )

        if not isinstance(importe, Decimal):
            raise ValueError("El importe debe ser de tipo Decimal.")

        if not importe.is_finite() or importe < 0:
            raise ValueError(
                "El importe debe ser un número válido y no negativo."
            )

        if type(fecha_pago) is not date:
            raise ValueError("La fecha de pago debe ser una fecha válida.")

        self.identificador = identificador
        self.importe = importe
        self.fecha_pago = fecha_pago

    def diferencias(self, otro_cheque):
        """Compara importe y fecha de dos cheques ya relacionados por ID."""

        errores = []

        if self.importe != otro_cheque.importe:
            errores.append("ERROR_IMPORTE")

        if self.fecha_pago != otro_cheque.fecha_pago:
            errores.append("ERROR_FECHA")

        return errores

    def diferencia_importe(self, otro_cheque):
        """Calcula importe del primer cheque menos importe del segundo."""

        return self.importe - otro_cheque.importe