# Matriz de pruebas de SIGEN Lite

Relaciona requisitos (RF/RNF), riesgos, casos de diseño TP de la guía (§6.3), la prueba automatizada que los ejecuta, el resultado esperado, el observado y la evidencia.

- **Ejecución registrada:** 10 de noviembre de 2026 (UTC 11-nov 04:5x), rama `stefven/calidad`, Windows 11, Python 3.11.18.
- **Comando:** `python scripts/verificar_calidad.py` → **255 aprobadas, 0 fallidas**, líneas 203/203, ramas 50/50. Evidencia: [evidencias/calidad/puerta_calidad.txt](evidencias/calidad/puerta_calidad.txt).
- **Contrato contra servidor real:** con Uvicorn (`--workers 1`) y `SIGEN_URL_BASE=http://127.0.0.1:8000`, las 118 pruebas de `tests/contract` también pasaron.
- La CI remota **no** se ha ejecutado (falta publicar la rama con autorización): la columna «Observado» corresponde a la ejecución local.

Abreviaturas de ubicación: **U** = `tests/unit/test_calculator.py` (Jose), **A** = `tests/api/test_api.py` (Jose), **C-éx / C-err / C-esq / C-500** = `tests/contract/test_contrato_{exito,errores,esquemas,fallo_interno}.py` (Stefven). Las pruebas de contrato no importan `sigen.config` ni `sigen.schemas`: usan constantes y esquemas propios (`tests/contract/contrato_esperado.py`, `tests/contract/esquemas/`).

## Riesgos considerados

| ID | Riesgo |
|---|---|
| R1 | Error `<`/`<=` en fronteras de nota o peso. |
| R2 | Coerción silenciosa de tipos (`"4.5"`, `true`, `30.0`). |
| R3 | Errores de coma flotante en el promedio o en la decodificación. |
| R4 | Política de redondeo aplicada al valor equivocado (promedio en vez de definitiva). |
| R5 | Ruptura del contrato HTTP (claves, tipos, códigos, Content-Type) que rompa la interfaz. |
| R6 | Exposición de trazas o datos de entrada en errores. |
| R7 | Regresión tras un cambio de mantenimiento. |
| R8 | Degradación o errores bajo concurrencia. |

## Casos TP de la guía

| TP | RF / riesgo | Datos | Esperado | Prueba concreta | Observado |
|---|---|---|---|---|---|
| TP-01 | RF-02 / R1 | nota 0.0 | Aceptar | C-éx `test_notas_frontera_validas[TP-01]`; A `test_notas_frontera_validas[0]`; U `test_notas_validas` | Aprobada |
| TP-02 | RF-02 / R1 | 0.1 | Aceptar | C-éx `test_notas_frontera_validas[TP-02]`; A ídem | Aprobada |
| TP-03 | RF-02 / R1 | -0.1 | 422 `RANGO` | C-err `test_nota_invalida[TP-03-negativa]`; A `test_notas_invalidas` | Aprobada |
| TP-04 | RF-02 / R1 | 5.0 | Aceptar | C-éx `test_notas_frontera_validas[TP-04]`, `test_tp08_tp09_umbral_de_aprobacion[maximo-5.0]` | Aprobada; **detecta** el defecto inducido `< 5.0` |
| TP-05 | RF-02 / R1 | 4.9 | Aceptar | C-éx `test_notas_frontera_validas[TP-05]` | Aprobada |
| TP-06 | RF-02 / R1 | 5.1 | 422 `RANGO` | C-err `test_nota_invalida[TP-06-mayor-5]` | Aprobada |
| TP-07 | RF-02 / R3 | 3.55 | 422 `PRECISION` | C-err `test_nota_invalida[TP-07-precision]`, `test_nota_invalida_en_cuerpo_bruto[precision-oculta]` | Aprobada |
| TP-08 | RF-05 / R4 | definitiva 2.9 | `REPROBADO` | C-éx `test_tp08_tp09_umbral_de_aprobacion[TP-08-definitiva-2.9]` | Aprobada |
| TP-09 | RF-05 / R4 | definitiva 3.0 | `APROBADO` | C-éx `test_tp08_tp09_umbral_de_aprobacion[TP-09-definitiva-3.0]`; U `test_estado_usa_definitiva` | Aprobada |
| TP-10 | RF-03 | 30+30+40 | Aceptar | C-éx `test_ponderaciones_validas[TP-10-30-30-40]` | Aprobada |
| TP-11 | RF-03 / R1 | 30+30+39 | 400 `SUMA_PESOS` | C-err `test_suma_de_pesos_distinta_de_100[TP-11-suma-99]` | Aprobada |
| TP-12 | RF-03 / R1 | 30+30+41 | 400 `SUMA_PESOS` | C-err `test_suma_de_pesos_distinta_de_100[TP-12-suma-101]` | Aprobada |
| TP-13 | RF-03 / R1 | un peso 0 | Aceptar | C-éx `test_ponderaciones_validas[TP-13-peso-cero]` | Aprobada |
| TP-14 | RF-03 / R1 | 100+0+0 | Aceptar | C-éx `test_ponderaciones_validas[TP-14-*]` | Aprobada |
| TP-15 | RF-03 / R1 | peso 101 | 422 `RANGO` | C-err `test_peso_invalido[TP-15-101]` | Aprobada |
| TP-16 | RF-02 / R2 | `"cuatro"` | 422 `TIPO` | C-err `test_nota_invalida[TP-16-texto]` | Aprobada |
| TP-17 | RF-02 / R2 | `null` | 422 `TIPO` | C-err `test_nota_invalida[TP-17-null]` | Aprobada |
| TP-18 | RF-02 / R2 | `true` | 422 `TIPO` | C-err `test_nota_invalida[TP-18-true]` | Aprobada |
| TP-19 | RF-01 | dos actividades | 422 `CANTIDAD` | C-err `test_cantidad_de_actividades[TP-19-dos]` | Aprobada |
| TP-20 | RF-01 | cuatro | 422 `CANTIDAD` | C-err `test_cantidad_de_actividades[TP-20-cuatro]` | Aprobada |
| TP-21 | RF-07 / R5 | petición válida | 200, 4 claves exactas, esquema | C-éx `test_tp21_tp24_ejemplo_de_la_guia` | Aprobada |
| TP-22 | RF-06 / R5 | petición inválida | 400/422 con envoltorio | Todas las de C-err validan `esquemas/error.schema.json` | Aprobada |
| TP-23 | RF-07 | `GET /health` | 200 cuerpo exacto | C-éx `test_tp23_salud_responde_contrato_exacto` | Aprobada |
| TP-24 | RF-04 | ejemplo 3.5/2.5/4.0 · 30/30/40 | 3.4 `APROBADO` | C-éx `test_tp21_tp24_ejemplo_de_la_guia`; U `test_ejemplo_aritmetico` | Aprobada |
| TP-25a | RF-05 / R3, R4 | bruto 2.949 | 2.9 `REPROBADO`; promedio exacto `2.949` | C-éx `test_tp25_frontera_de_redondeo[TP-25a-2.949]` | Aprobada |
| TP-25b | RF-05 / R3, R4 | bruto 2.950 | 3.0 `APROBADO` | C-éx `[TP-25b-2.950]` | Aprobada |
| TP-25c | RF-05 / R3, R4 | bruto 2.951 | 3.0 `APROBADO` | C-éx `[TP-25c-2.951]` | Aprobada |
| TP-26 | RNF-06 / R7 | defecto inducido `< 5.0` en copia aislada | Falla antes, pasa después | Procedimiento de [mantenimiento.md](mantenimiento.md) | 6 fallos → 255 aprobadas. [Evidencia](evidencias/mantenimiento/) |
| TP-27 | RF-02/03 / R2 | `"4.5"`, `"30"`, `true`, `30.0`, `3e1` | 422 `TIPO` | C-err `test_nota_invalida[TP-27-*]`, `test_peso_invalido[TP-27-*]`, `test_tp27_peso_con_token_no_entero_se_rechaza` | Aprobada |
| TP-28 | RF-02 | `3`, `3.0`, `3.50`, `35e-1`, `0.35E1` | Aceptar | C-éx `test_tp28_escritura_numerica_equivalente` | Aprobada |
| TP-29 | RF-01 | faltantes, extras, blancos, 1/80/81 caracteres | `REQUERIDO`, `CAMPO_DESCONOCIDO`, `LONGITUD` | C-err `test_tp29_*`, `test_campo_adicional_*`, `test_nota_requerida_aunque_el_peso_sea_cero`; C-éx `test_tp29_nombres_validos` | Aprobada |
| TP-30 | RF-02 / R6 | JSON roto, NaN, ±Infinity, bytes no UTF-8 (cuerpo bruto) | 422 `body`/`JSON_INVALIDO` | C-err `test_tp30_cuerpo_no_json_valido`, `test_tp30_bytes_que_no_son_utf8` | Aprobada |
| TP-31 | RNF-03 / R6 | excepción sustituida con `monkeypatch` | 500 `ERROR_INTERNO`, `campos: []`, sin detalles | C-500 `test_tp31_fallo_interno_responde_500_generico` | Aprobada |

## Comprobaciones adicionales de contrato

| Requisito / riesgo | Comprobación | Prueba | Observado |
|---|---|---|---|
| RF-07 / R5, R3 | Promedio y definitiva son números JSON (no cadenas) y su valor decimal emitido es exacto | C-éx `test_numeros_se_emiten_como_numeros_json_y_no_como_cadenas`, TP-25 con `Decimal` | Aprobada |
| RF-06 / R5 | 400 solo tras validar campos: suma 110 + nota 5.1 ⇒ solo 422 | C-err `test_errores_de_campo_tienen_precedencia_sobre_la_suma` | Aprobada |
| RF-06 | Varios errores a la vez, comparados como conjunto (sin orden) | C-err `test_varios_errores_se_informan_juntos` | Aprobada |
| RNF-03 / R6 | Errores no repiten valores de la petición ni trazas | C-err `test_error_no_refleja_valores_de_la_peticion` | Aprobada |
| RF-02 | `1e1000` es JSON válido pero fuera de rango ⇒ `RANGO` | C-err `test_nota_invalida_en_cuerpo_bruto[numero-json-enorme]` | Aprobada |
| RF-08 | Peticiones sucesivas no comparten estado | C-éx `test_rf08_recalcular_no_conserva_estado_entre_peticiones` | Aprobada |
| Integración | `/`, `/static`, `/openapi.json` conviven con la API | C-éx `test_interfaz_y_documentacion_conviven_con_la_api` | Aprobada |
| JSON Schema | Esquemas declaran Draft 2020-12, son válidos y rechazan propiedades adicionales | C-esq `test_esquema_declara_version_y_es_valido`, `test_esquemas_rechazan_propiedades_adicionales` | Aprobada |
| JSON Schema (límite) | Con floats, el esquema acepta `30.0` como entero; el servidor lo rechaza | C-esq `test_esquema_con_floats_no_distingue_30_de_30_0` | Aprobada |
| JSON Schema (límite) | `multipleOf: 0.1` solo es fiable decodificando con `Decimal` | C-esq `test_multipleof_exacto_al_decodificar_con_decimal` | Aprobada |
| JSON Schema (límite) | El esquema no verifica la suma de pesos ni la longitud recortada | C-esq `test_esquema_no_basta_para_la_suma_de_pesos`, `test_esquema_no_aplica_la_longitud_tras_recortar` | Aprobada |
| RNF-04 | La puerta usa líneas, no el combinado; falla sin reporte o con 0 sentencias | `tests/calidad/test_verificar_calidad.py` (18 casos) | Aprobada |
| RNF-05 / R8 | Carga 10/20/50 usuarios con verificación de cuerpo | `locustfile.py` | Ver [reporte_calidad.md](reporte_calidad.md#6-pruebas-de-carga) |

## Pendiente

- Ejecución en GitHub Actions (requiere push autorizado).
- Pruebas de interfaz: responsabilidad de Santiago, registradas en [pruebas_interfaz.md](pruebas_interfaz.md).
