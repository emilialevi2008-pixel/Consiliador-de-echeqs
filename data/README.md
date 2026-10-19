# Datos de prueba del conciliador

## Procedencia

Se utilizarán datos ficticios generados para este trabajo.
No se incluirán datos bancarios reales ni información personal sensible.

Responsable: Emilia Agustina Levi.

## Qué representa cada fila

Cada fila representa un registro de un cheque en el archivo del
banco o del sistema de gestión. Puede haber registros duplicados.

## Columnas del sistema

- ID CHEQUE: identificador del cheque.
- FECHA DE EMISION: fecha en que se emitió.
- FECHA DE COBRO: fecha prevista para cobrarlo.
- BANCO: banco indicado en el sistema.
- TITULAR: titular registrado.
- IMPORTE: valor del cheque en pesos argentinos.

## Columnas del banco

- ID Cheque: identificador del cheque.
- Nombre o Razón Social Emisor: emisor registrado.
- Historial de Endosos: información de los endosos.
- Fecha Emisión: fecha en que se emitió.
- Fecha Pago: fecha prevista para pagarlo.
- Importe: valor del cheque en pesos argentinos.

## Reglas de comparación

Se compararán el identificador, el importe y la fecha de cobro
del sistema con la fecha de pago del banco.

Las fechas se mostrarán en DD/MM/AAAA.
Los identificadores se conservarán como texto.
Los importes se calcularán con Decimal para evitar errores de precisión.

## Limitaciones

Los datos ficticios servirán para probar el programa.
No representan operaciones reales ni permiten sacar conclusiones
sobre la actividad de un banco.