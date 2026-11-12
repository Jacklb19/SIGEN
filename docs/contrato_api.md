# Contrato inicial de SIGEN Lite

Este documento concreta las secciones 2 y 5 de `SIGEN_Lite_Guia_Completa.md`. Implementación del frente de Jose, versión 0.1.0. No implica revisión ya realizada por Santiago o Stefven. Cualquier cambio incompatible debe coordinarse entre los tres.

## Salud

`GET /health` devuelve HTTP 200, `Content-Type: application/json` y exactamente:

```json
{"status":"ok","service":"sigen-lite"}
```

## Cálculo

`POST /api/v1/calcular` recibe un objeto JSON con única clave `actividades` y exactamente tres objetos con `nombre`, `nota` y `peso`.

```json
{
  "actividades": [
    {"nombre":"Parcial 1","nota":3.5,"peso":30},
    {"nombre":"Parcial 2","nota":2.5,"peso":30},
    {"nombre":"Proyecto","nota":4.0,"peso":40}
  ]
}
```

| Campo | Regla |
|---|---|
| nombre | Cadena requerida, recortada en los extremos, de 1 a 80 caracteres. Se permiten duplicados. |
| nota | Número JSON finito entre 0 y 5, múltiplo de 0.1. Se aceptan enteros y escrituras equivalentes como 3.50 y 35e-1. |
| peso | Token entero JSON entre 0 y 100. Se rechazan 30.0, notación exponencial, booleanos, cadenas y nulos como pesos. |
| Total de pesos | Exactamente 100, después de validar todos los campos. |

No se aceptan claves adicionales, cadenas numéricas, booleanos ni nulos en notas. Las tres notas son requeridas aunque algún peso sea cero. Un campo vacío no se interpreta como cero.

### Resultado HTTP 200

```json
{
  "promedio_ponderado":3.4,
  "nota_definitiva":3.4,
  "estado":"APROBADO",
  "ponderacion_total":100
}
```

Se emiten exactamente esas cuatro claves. Promedio y definitiva son números JSON, no cadenas; total es entero. El promedio bruto no se redondea durante el cálculo. La definitiva se obtiene con Decimal y ROUND_HALF_UP a un decimal; APROBADO si la definitiva es al menos 3.0, REPROBADO en caso contrario. Es política asumida del prototipo, no regla institucional certificada. La interfaz debe mostrar un decimal, pues JSON no garantiza conservar ceros finales.

### Errores

```json
{
  "error": {
    "codigo":"VALIDACION",
    "mensaje":"Revisa los datos.",
    "campos":[
      {"ruta":"actividades.0.nota","codigo":"RANGO","mensaje":"La nota debe estar entre 0 y 5 y ser finita."}
    ]
  }
}
```

| HTTP | Código general | Ruta / código de campo |
|---|---|---|
| 422 | VALIDACION | JSON inválido: body / JSON_INVALIDO |
| 422 | VALIDACION | Campo faltante: ruta del campo / REQUERIDO |
| 422 | VALIDACION | Tipo incompatible: ruta del campo o body / TIPO |
| 422 | VALIDACION | Rango inválido: ruta del campo / RANGO |
| 422 | VALIDACION | Nota no múltiplo de 0.1: ruta del campo / PRECISION |
| 422 | VALIDACION | Nombre vacío o demasiado largo tras recortar: ruta del campo / LONGITUD |
| 422 | VALIDACION | Campo adicional: ruta de la clave / CAMPO_DESCONOCIDO |
| 422 | VALIDACION | Cantidad de actividades: actividades / CANTIDAD |
| 400 | PONDERACION_INVALIDA | actividades.pesos / SUMA_PESOS |
| 500 | ERROR_INTERNO | Lista campos vacía, mensaje genérico |

Las rutas usan índices desde cero. Se pueden devolver varios errores; no depender de su orden ni del texto literal. Si hay errores de campo, no comprobar todavía la suma. No se devuelven valores de entrada, trazas o excepciones internas.

JSON mal formado, NaN e infinitos literales se rechazan antes de validar campos, con JSON_INVALIDO. Un número JSON válido pero fuera de rango, como `1e1000`, se rechaza con RANGO. Estas respuestas tienen `Content-Type: application/json`. Las rutas inexistentes y otros errores ajenos a estos endpoints mantienen el tratamiento HTTP normal de FastAPI.

## Precisión, esquemas y documentación

La API usa `json.loads(..., parse_float=Decimal)` y rechaza constantes no JSON; los enteros se mantienen como int y los booleanos se validan por tipo exacto. No se construye Decimal desde un float. Una nota válida se normaliza a una cifra decimal antes de operar. El promedio de estas notas y pesos enteros requiere como máximo tres decimales.

La conversión a float ocurre únicamente al representar el resultado HTTP; no participa en el cálculo, redondeo o decisión académica. Las pruebas verifican la respuesta numérica y las fronteras por HTTP real dentro del cliente de pruebas ASGI.

`GET /openapi.json` y `/docs` describen entrada, salida y errores. Los esquemas de `src/sigen/schemas.py` usan JSON Schema compatible con Draft 2020-12 / OpenAPI 3.1 y restricciones obtenidas de `config.py`. Hay reglas adicionales del servidor: suma de pesos, distinción de token entero y longitud después de recortar el nombre. El esquema documenta esa normalización; no impone un máximo sobre el texto sin recortar que rechazara entradas válidas como un nombre de 80 caracteres rodeado de espacios.

Al verificar multipleOf=0.1 con una biblioteca que utiliza floats binarios, decodificar números y esquema con Decimal para evitar falsos negativos del propio verificador. Esta precaución no debe cambiar el contrato ni permitir strings numéricos.

## Interfaz y estáticos

- `/` sirve `src/sigen/web/index.html`.
- `/static` expone los recursos de la interfaz incluidos en el paquete.
- El montaje no intercepta `/health`, `/api/v1/calcular` ni `/docs`.
- Santiago usa URLs relativas del mismo origen. La aplicación no necesita CORS para esa arquitectura.

No se implementa RF-09 ni persistencia, autenticación o integración institucional.
