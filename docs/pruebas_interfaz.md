# Pruebas de la interfaz

El cierre del 11 de noviembre añade tres regresiones automatizadas en
`tests/ui/test_interfaz.cjs`. Cubren precisión oculta, ceros finales y foco
tras 422. Las tres aprobaron con la corrección. El historial de la reparación
está en [mantenimiento.md](mantenimiento.md).

Registro de las comprobaciones reales del frente de interfaz de SIGEN Lite.
Fecha: 10 de noviembre de 2026. Rama: `santiago/interfaz`.

## Entorno

- Backend real del repositorio (`src/sigen/api.py`) servido con
  `uvicorn sigen.api:app --app-dir src` en `http://localhost:8123/`.
- Python 3.12.16 en `.venv` local con las dependencias fijadas de
  `docs/backend.md` (fastapi 0.162.4, pydantic 2.14.3, starlette 1.10.0).
  Diferencia con lo documentado: `docs/backend.md` verificó Python 3.11.16;
  aquí se usó 3.12.16. Las 119 pruebas del backend pasaron igualmente y la
  API respondió según el contrato, pero queda anotada la diferencia.
- Navegador: Chromium incrustado del cliente de escritorio (motor Chrome),
  con interacción real sobre la página (clics, escritura y teclado) e
  inspección del DOM.
- Tamaños de pantalla comprobados: escritorio (panel del navegador incrustado)
  y móvil emulado a 390 × 844 px.
- Antes de la interfaz se verificó la línea base del backend: 119 pruebas
  aprobadas y 100 % de cobertura (203/203 sentencias, 50/50 ramas), con la
  advertencia conocida de Starlette/httpx que evaluará Stefven.

## Comprobaciones realizadas

| # | Escenario | Método | Resultado |
|---|---|---|---|
| 1 | `GET /health` responde el JSON exacto del contrato | curl | ✅ `{"status":"ok","service":"sigen-lite"}` |
| 2 | `GET /` sirve la interfaz (antes 404) | curl | ✅ HTTP 200 con el HTML propio |
| 3 | `GET /static/styles.css` y `/static/app.js` | curl | ✅ HTTP 200 ambos |
| 4 | Ejemplo del contrato: 3.4 y APROBADO | curl y navegador | ✅ `promedio_ponderado` 3.4, `nota_definitiva` 3.4, APROBADO; en pantalla se muestran ambos valores, el estado y la nota sobre el redondeo |
| 5 | Redondeo 2.95 → 3.0 (notas 3.0/3.5/2.5, pesos 30/30/40) | curl | ✅ `promedio_ponderado` 2.95, `nota_definitiva` 3.0, APROBADO |
| 6 | Pesos que suman 110 → 400 PONDERACION_INVALIDA | curl y navegador | ✅ API: `actividades.pesos` / SUMA_PESOS. Pantalla: mensaje "Los pesos deben sumar 100." junto al total ("110 / 100") y resumen general |
| 7 | Nota 5.1 → 422 RANGO | curl y navegador | ✅ API: `actividades.0.nota` / RANGO. En pantalla la validación local ya lo impide con mensaje bajo el campo, `aria-invalid` y foco en el campo; no se envía la petición |
| 8 | Campo de nota vacío → 422 | curl y navegador | ✅ API: `actividades.0.nota` / TIPO al enviar `""`. En pantalla la validación local lo reporta como obligatorio sin convertirlo en cero |
| 9 | Estado de carga y sin envíos duplicados | navegador | ✅ Al enviar, el botón muestra "Calculando…" con campos y botones deshabilitados; se restauran al terminar |
| 10 | Resultado desactualizado al editar | navegador | ✅ Tras un cálculo exitoso, editar una nota marca el panel como "Resultado anterior: los datos cambiaron desde este cálculo." |
| 11 | Restablecer | navegador | ✅ Repone Parcial 1/3.5/30, Parcial 2/2.5/30, Proyecto/4.0/40, limpia errores y resultado, y mueve el foco al primer campo |
| 12 | Navegación por teclado | navegador (teclas Tab reales) | ✅ El foco recorre nombre → nota → peso de cada actividad en orden visual |
| 13 | Diseño móvil a 390 px | navegador (emulación de dispositivo) | ✅ Las actividades se apilan en tarjetas, se ocultan los encabezados de columna y las etiquetas quedan visibles |
| 14 | Error de conexión | navegador con el servidor detenido | ✅ Mensaje "No fue posible comunicarse con el servidor…", controles restaurados y sin resultado falso |

## Pendientes y limitaciones

- **Error de servidor (500 ERROR_INTERNO)**: no se pudo reproducir; provocarlo
  exigiría modificar el backend de Jose, lo cual está fuera del alcance. El
  manejo está implementado (mensaje genérico sin trazas) pero queda **sin
  verificar en vivo**.
- **Captura de pantalla**: la herramienta de captura del navegador incrustado
  agotó su tiempo de espera; la verificación visual se hizo por inspección del
  DOM y estilos calculados, sin imagen adjunta.
- **Otros navegadores**: solo se comprobó en el motor Chromium incrustado;
  Firefox y Safari quedan pendientes.
- **Lectores de pantalla**: los atributos de accesibilidad (`aria-live`,
  `aria-invalid`, `aria-describedby`, etiquetas) están implementados, pero no
  se verificaron con un lector real.
- No se añadieron dependencias de E2E; cualquier suite automatizada de
  interfaz debe coordinarse con Stefven.
