# Conciliador de cheques electrónicos

Autora: Emilia Agustina Levi.

Trabajo Práctico 2 — Programación Orientada a Datos.
Licenciatura en Ciencia de Datos — UCA.

## Problema, usuarios y solución

Comparar manualmente los cheques de un banco con los registrados en
un sistema de gestión lleva tiempo y puede producir errores.

La aplicación está destinada a personas que realizan tareas
administrativas o contables. Permite cargar dos archivos, comparar
los cheques y obtener reportes de coincidencias, diferencias,
registros sin contraparte y datos que requieren revisión.

## Funcionalidades

- Leer archivos CSV, JSON y Excel .xlsx.
- Validar identificadores, importes y fechas.
- Comparar identificadores completos y abreviados.
- Detectar diferencias de importe y fecha de pago.
- Informar duplicados, datos inválidos y coincidencias ambiguas.
- Calcular totales monetarios mediante Decimal.
- Guardar reportes y un registro de modificaciones y rechazos.

La aplicación procesa los registros de los archivos indicados.
No tiene fechas, importes ni identificadores de trabajo fijos.
Las fechas pueden pertenecer a distintos meses y años.

## Instalación

El entorno utilizado durante el desarrollo es Python 3.14.5 en macOS.

Abrir una terminal dentro de la carpeta principal del proyecto y ejecutar:

```bash
python3 -m pip install -r requirements.txt
```

La dependencia adicional es openpyxl, utilizada para leer Excel.
Las demás bibliotecas utilizadas pertenecen a Python.

## Ejecución con datos ficticios

Primero generar los archivos de ejemplo:

```bash
python3 -m src.generar_datos
```

Después ejecutar la comparación:

```bash
python3 -m src.main --banco data/ejemplos/banco.csv --sistema data/ejemplos/sistema.json
```

Los reportes se guardan en `outputs`.

Para consultar las opciones:

```bash
python3 -m src.main --help
```

## Uso con otros archivos

Los dos archivos pueden tener formatos diferentes.
Cada ruta debe señalar un archivo existente.

Ejemplo de uso, reemplazando las rutas por las propias:

```bash
python3 -m src.main --banco "ruta/banco.xlsx" --sistema "ruta/sistema.csv" --salida "outputs/otra_comparacion"
```

Si una ruta contiene espacios, debe escribirse entre comillas.

Se recomienda utilizar una carpeta de salida diferente para cada
comparación que se quiera conservar. Una nueva ejecución sobre
la misma carpeta reemplaza los cuatro reportes anteriores.

## Estructura de entrada

Columnas obligatorias del banco:

- `ID Cheque`
- `Importe`
- `Fecha Pago`

Columnas obligatorias del sistema:

- `ID CHEQUE`
- `IMPORTE`
- `FECHA DE COBRO`

Los encabezados deben respetar los nombres indicados.

Los archivos pueden contener columnas complementarias, como emisor,
titular, banco, fecha de emisión e historial de endosos.
Estas columnas no determinan automáticamente la conciliación.

El CSV debe utilizar coma como separador y encabezados en la primera fila.
Los valores que contengan comas deben ir entre comillas.

El JSON debe contener una lista de objetos.

Para Excel se utiliza la primera hoja y sus encabezados deben estar
en la primera fila. Se admite .xlsx; no se admite el formato antiguo .xls.
Se recomienda que los campos comparados contengan valores, porque
openpyxl no calcula fórmulas de Excel.

Los identificadores deben almacenarse como texto, especialmente
si contienen ceros iniciales.

Los importes deben estar expresados en la misma moneda y sin separadores
de miles. Se admite punto o coma decimal, con hasta dos decimales.

Las fechas de texto admitidas son DD/MM/AAAA y AAAA-MM-DD.
También se admiten fechas nativas de Excel.

## Reglas de comparación

Se busca primero una coincidencia exacta de identificador.

Cuando no existe, el identificador del sistema puede corresponder
al comienzo del identificador bancario. La coincidencia debe ser única
y no debe reutilizar un registro ya asignado.

No se supone una longitud fija para los identificadores.
Se distinguen mayúsculas y minúsculas.

Después de identificar el par se comparan el importe y la fecha de pago.
`FECHA DE COBRO` del sistema se compara con `Fecha Pago` del banco.

Los identificadores duplicados y las coincidencias ambiguas
requieren revisión y no se concilian automáticamente.
Los rechazos con identificadores reconocibles también se consideran
para evitar coincidencias inseguras.

## Limpieza y validación

Se quitan espacios al principio y al final del identificador.
Los identificadores deben contener únicamente letras sin tildes y números.

Los importes se convierten a Decimal para evitar errores de cálculo
propios de la representación binaria de números decimales.
Se rechazan importes negativos, faltantes, no numéricos o con más
de dos decimales. No se reemplazan por cero.

Las fechas se convierten a objetos de fecha.
Además de reconocer el formato, se comprueba que existan en el calendario.
Si una fecha nativa contiene hora, se conserva solamente el día.

No se corrigen automáticamente fechas imposibles ni se eliminan
duplicados para forzar una coincidencia.

El registro de auditoría conserva las filas modificadas o rechazadas,
sus datos originales y los cambios o motivos correspondientes.
Se guarda dentro de `resumen.json`.

La referencia de fila comienza en 1 para el primer registro de datos,
sin contar el encabezado del CSV o Excel.

## Archivos de salida

- `reporte_conciliacion.csv`: todos los resultados.
- `cheques_con_errores.csv`: resultados que requieren revisión.
- `resumen.json`: cantidades por estado, importes y auditoría.
- `resumen_importes.csv`: tabla de totales monetarios.

Los estados principales son:

| Estado | Interpretación |
| --- | --- |
| CONCILIADO | Coinciden ID completo, importe y fecha |
| CONCILIADO_ID_ABREVIADO | Coincidencia por ID abreviado, importe y fecha |
| ERROR_IMPORTE | El par tiene importes diferentes |
| ERROR_FECHA | El par tiene fechas diferentes |
| CON_DIFERENCIAS | Difieren el importe y la fecha |
| NO_ESTA_EN_BANCO | No se encontró una contraparte bancaria |
| NO_ESTA_EN_SISTEMA | No se encontró una contraparte en el sistema |
| ID_DUPLICADO | El identificador está repetido en una fuente |
| COINCIDENCIA_AMBIGUA | No se puede asignar una contraparte única |
| DATOS_INVALIDOS | Un registro no superó la validación |
| PENDIENTE_REVISION | Hay una posible relación que no permite conciliar automáticamente |

Cada resultado puede representar un par de registros o un registro
individual. Por eso la cantidad de resultados no equivale necesariamente
a la cantidad de filas de entrada ni de cheques distintos.

## Interpretación de los importes

Los totales brutos suman todos los importes válidos de cada archivo,
aunque existan errores en otros campos o identificadores duplicados.
Las exclusiones por importe inválido y los duplicados incluidos
se detallan en el resumen.

La diferencia se calcula como:

    total del banco - total del sistema

El importe conciliado cuenta una sola vez cada par conciliado.
Los importes de pares con diferencias se muestran por separado
para cada fuente.

Una diferencia global de cero no garantiza la conciliación:
las diferencias individuales pueden compensarse.

## Ejemplo de resultado

Con los datos producidos por el generador incluido:

- Registros bancarios: 101.
- Registros del sistema: 100.
- Pares conciliados: 90.
- Total bruto bancario: 228851.50.
- Total bruto del sistema: 228958.00.
- Diferencia: -106.50.

Los casos problemáticos son intencionales y permiten verificar
el comportamiento de la aplicación.

## Pruebas

Desde la carpeta principal:

```bash
python3 -m unittest discover -s tests -v
```

Las pruebas incluyen casos normales, entradas inválidas, equivalencia
de lectura CSV/JSON, lectura Excel, precisión monetaria, fechas,
duplicados, ambigüedades y generación de reportes.

También comprueban que cada fila de entrada conserve una referencia
en los resultados y que un mismo registro no se cuente dos veces.

## Datos y procedencia

Los ejemplos se generan mediante `src/generar_datos.py`, sin utilizar
datos bancarios reales ni números aleatorios.

Cada fila representa un registro de un cheque en una fuente.
Las condiciones de uso, variables, cantidades y limitaciones
están documentadas en [data/README.md](data/README.md).

## Organización y decisiones de diseño

- `src/fuentes.py`: interfaz FuenteDatos y lectores CSV, JSON y Excel.
- `src/modelos.py`: clase ChequeElectronico.
- `src/validaciones.py`: conversión y validación de fechas e importes.
- `src/pipeline.py`: preparación de registros y comparación de pares.
- `src/conciliacion.py`: asignación de contrapartes y tratamiento de conflictos.
- `src/importes.py`: totales y controles monetarios.
- `src/reportes.py`: exportación de resultados.
- `src/generar_datos.py`: construcción de ejemplos reproducibles.
- `src/main.py`: argumentos y coordinación del programa.
- `tests/`: pruebas automatizadas.
- `data/`: documentación y ejemplos ficticios.

ChequeElectronico reúne atributos del dominio y métodos para comparar
importe y fecha.

FuenteDatos establece una interfaz común: cada lector implementa
cargar(ruta) y devuelve una lista de diccionarios. Así, la comparación
puede trabajar sin depender del formato original.

Las expresiones regulares comprueban el patrón alfanumérico del ID
y la estructura textual del importe. Se complementan con conversiones
y controles de calendario, signo y precisión.

## Alcance y limitaciones

Es una herramienta de apoyo a la revisión administrativa.
No comprueba la autenticidad ni la situación legal de un cheque.

No se conecta automáticamente con bancos ni sistemas de gestión,
no modifica sus registros y no realiza operaciones bancarias.

No convierte monedas ni compara automáticamente nombres,
historiales de endosos o fechas de emisión.

Los ejemplos permiten probar reglas conocidas, pero no demuestran
el desempeño sobre todos los formatos de exportación de bancos reales.
Otros encabezados o estructuras requieren una adaptación documentada.

El uso de identificadores abreviados depende de que esa relación
sea válida en las fuentes utilizadas. Los casos inseguros se revisan
manualmente.

Los archivos privados, credenciales y datos personales sensibles
no deben subirse al repositorio.