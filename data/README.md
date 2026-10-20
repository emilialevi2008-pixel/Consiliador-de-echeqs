# Datos de prueba

## Procedencia

Los archivos son ficticios y se generan con `src/generar_datos.py`.
No provienen de cuentas bancarias ni de personas reales.

Responsable del conjunto de prueba: Emilia Agustina Levi.
Fecha de documentación: 20/10/2026.
No corresponde una URL ni fecha de consulta externa porque los datos
se construyen mediante un procedimiento incluido en el proyecto.

Condiciones de uso: los ejemplos se pueden utilizar y modificar
para pruebas y actividades educativas. No representan operaciones reales.

## Generación reproducible

Desde la carpeta principal del proyecto:

    python3 -m src.generar_datos

El comando crea:

- `data/ejemplos/banco.csv`: 101 registros.
- `data/ejemplos/sistema.json`: 100 registros.

El procedimiento no utiliza números aleatorios. Al repetirlo se obtienen
los mismos datos y se reemplazan estos dos archivos de ejemplo.

## Unidad de análisis

Cada fila u objeto representa un registro de un cheque electrónico
en una fuente. Un mismo cheque puede aparecer en ambas fuentes.

Se agregan duplicados intencionales para probar su detección.

## Variables bancarias

| Columna | Contenido |
| --- | --- |
| ID Cheque | Identificador alfanumérico del cheque |
| Nombre o Razón Social Emisor | Nombre ficticio del emisor |
| Historial de Endosos | Información complementaria ficticia |
| Fecha Emisión | Fecha de emisión |
| Fecha Pago | Fecha de pago utilizada en la comparación |
| Importe | Importe monetario del registro |

## Variables del sistema

| Columna | Contenido |
| --- | --- |
| ID CHEQUE | Identificador completo o abreviado |
| FECHA DE EMISION | Fecha de emisión |
| FECHA DE COBRO | Fecha comparada con Fecha Pago del banco |
| BANCO | Nombre ficticio del banco |
| TITULAR | Nombre ficticio del titular |
| IMPORTE | Importe monetario del registro |

## Formatos y unidades

Los importes de prueba representan pesos argentinos y se expresan
sin separadores de miles, con hasta dos decimales.

Las fechas de texto se expresan como DD/MM/AAAA.
El programa también admite fechas ISO AAAA-MM-DD y fechas nativas de Excel.

Los identificadores se conservan como texto para mantener letras
y posibles ceros iniciales.

El CSV utiliza coma como separador y una primera fila con encabezados.
El JSON contiene una lista de objetos.
Para Excel se admite .xlsx, con encabezados en la primera fila
de la primera hoja.

## Casos incluidos

Hay coincidencias exactas, identificadores abreviados, diferencias de
importe y fecha, registros sin contraparte, duplicados y datos inválidos.

Los errores son intencionales: permiten comprobar que el programa
los informa y conserva la referencia al registro original.

## Limitaciones

Los ejemplos sirven para verificar reglas del programa; no representan
la distribución de operaciones de un banco ni permiten medir su precisión
sobre datos bancarios reales.

El historial de endosos y los nombres son información complementaria:
no se utilizan como criterios automáticos de conciliación.

La comparación supone que ambos archivos expresan importes en la misma
moneda. El programa no convierte monedas.
