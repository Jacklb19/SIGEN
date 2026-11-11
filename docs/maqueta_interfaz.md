# Maqueta de la interfaz de SIGEN Lite

Propuesta visual y plan de implementación del frente de interfaz (Santiago).
Estado: **pendiente de aprobación de Jose**. No se implementará HTML/CSS/JS hasta
recibir aprobación explícita.

Base contractual: `docs/contrato_api.md` (secciones de cálculo, errores y
estáticos) y `SIGEN_Lite_Guia_Completa.md` (secciones 2 y 5).

## 1. Alcance de la pantalla

- Una sola pantalla, en español, adaptable a móvil y escritorio, sin framework.
- Tres filas de actividad con: nombre, nota y peso.
- Valores iniciales acordados:

  | Actividad | Nota | Peso |
  |---|---|---|
  | Parcial 1 | 3.5 | 30 |
  | Parcial 2 | 2.5 | 30 |
  | Proyecto | 4.0 | 40 |

- Total de pesos visible y actualizado al editar (solo informativo; la suma la
  valida el servidor).
- Botones: **Calcular definitiva** y **Restablecer**.
- Resultado: promedio ponderado, definitiva con exactamente un decimal y estado
  APROBADO/REPROBADO, con la nota aclaratoria de que el redondeo es una política
  del simulador académico, no una regla institucional certificada.
- Consumo de `POST /api/v1/calcular` con URL relativa y recursos bajo `/static`,
  mismo origen servido por FastAPI.

## 2. Maqueta de escritorio (≥ 768 px)

```text
┌────────────────────────────────────────────────────────────────────┐
│  SIGEN Lite                                                        │
│  Simulador de definitiva académica                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Actividades                                                       │
│  ┌──────────────────┬────────────────────┬──────────────────────┐  │
│  │ Actividad        │ Nota (0.0 – 5.0)   │ Peso (0 – 100)       │  │
│  ├──────────────────┼────────────────────┼──────────────────────┤  │
│  │ [Parcial 1     ] │ [3.5]              │ [30]                 │  │
│  │ [Parcial 2     ] │ [2.5]              │ [30]                 │  │
│  │ [Proyecto      ] │ [4.0]              │ [40]                 │  │
│  └──────────────────┴────────────────────┴──────────────────────┘  │
│  Total de pesos: 100 / 100                                         │
│                                                                    │
│  [ Calcular definitiva ]   [ Restablecer ]                         │
│                                                                    │
│  ┌─ Resultado ─────────────────────────────────────────────────┐   │
│  │ Promedio ponderado: 3.4    Definitiva: 3.4                  │   │
│  │ Estado: APROBADO                                            │   │
│  │ El redondeo a un decimal es una política de este simulador, │   │
│  │ no una regla institucional certificada.                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

- Ancho máximo de contenido ~720 px, centrado, con margen lateral generoso.
- El panel de resultado solo aparece tras una respuesta exitosa; no ocupa
  espacio permanente en el estado inicial.
- Los mensajes de error por campo se muestran bajo el campo correspondiente y
  el campo queda marcado con borde de error más texto (no solo color).

## 3. Maqueta de móvil (< 768 px)

Las tres columnas se apilan en una tarjeta por actividad; las etiquetas van
encima de cada campo.

```text
┌──────────────────────────────┐
│ SIGEN Lite                   │
│ Simulador de definitiva      │
├──────────────────────────────┤
│ Actividad 1                  │
│ Nombre                       │
│ [Parcial 1                 ] │
│ Nota (0.0 – 5.0)             │
│ [3.5                       ] │
│ Peso (0 – 100)               │
│ [30                        ] │
│                              │
│ Actividad 2                  │
│ Nombre                       │
│ [Parcial 2                 ] │
│ Nota (0.0 – 5.0)             │
│ [2.5                       ] │
│ Peso (0 – 100)               │
│ [30                        ] │
│                              │
│ Actividad 3                  │
│ Nombre                       │
│ [Proyecto                  ] │
│ Nota (0.0 – 5.0)             │
│ [4.0                       ] │
│ Peso (0 – 100)               │
│ [40                        ] │
│                              │
│ Total de pesos: 100 / 100    │
│                              │
│ [ Calcular definitiva ]      │
│ [ Restablecer ]              │
│                              │
│ ┌─ Resultado ──────────────┐ │
│ │ Promedio ponderado: 3.4  │ │
│ │ Definitiva: 3.4          │ │
│ │ Estado: APROBADO         │ │
│ │ (nota sobre redondeo)    │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

- Campos de altura cómoda al tacto (≥ 44 px), botones a ancho completo.
- El orden de tabulación sigue el orden visual: nombre, nota, peso de cada
  actividad, luego los botones.

## 4. Estados principales

### 4.1 Inicial

- Formulario con los valores iniciales de la sección 1.
- Sin resultado ni mensajes de error.
- Total de pesos: "100 / 100".

### 4.2 Cálculo en curso

- Botón **Calcular definitiva** deshabilitado con texto "Calculando…" y un
  indicador de actividad visible (no solo un cambio de color).
- Todos los campos y el botón **Restablecer** deshabilitados para evitar envíos
  duplicados.
- Se restauran los controles tanto en éxito como en fallo.

### 4.3 Éxito (HTTP 200)

- Panel de resultado con promedio ponderado, definitiva con exactamente un
  decimal (p. ej. `3.0`, no `3`) y estado APROBADO o REPROBADO.
- El estado usa color como apoyo, siempre acompañado del texto.
- El panel se anuncia a lectores de pantalla (región con `aria-live`).

### 4.4 Errores por campo (HTTP 422, código VALIDACION)

- Cada entrada de `error.campos` se ubica bajo su campo usando la ruta
  `actividades.<índice>.<campo>` (índice desde cero).
- El campo afectado recibe borde de error, `aria-invalid="true"` y el mensaje
  se asocia con `aria-describedby`.
- Un resumen general ("Revisa los datos.") aparece sobre el formulario y mueve
  el foco al primer campo con error.
- Errores sin ruta reconocible (p. ej. `body`) se muestran en el resumen
  general.
- No se depende del orden de los errores ni de su texto literal.

### 4.5 Ponderación inválida (HTTP 400, PONDERACION_INVALIDA)

- La ruta `actividades.pesos` (suma) se muestra como mensaje junto al total de
  pesos, p. ej. "Los pesos deben sumar 100 (actual: 110).", además del resumen
  general.

### 4.6 Error de servidor (HTTP 500, ERROR_INTERNO)

- Mensaje genérico y humano: "Ocurrió un error interno. Intenta de nuevo más
  tarde." Sin trazas técnicas ni detalles de la excepción.

### 4.7 Error de conexión o respuesta inesperada

- Fallo de red, tiempo de espera o JSON con forma distinta a la del contrato:
  "No fue posible comunicarse con el servidor. Revisa tu conexión e intenta de
  nuevo."

### 4.8 Resultado desactualizado

- Si el usuario edita cualquier campo después de un cálculo, el panel de
  resultado se marca como desactualizado (texto "Resultado anterior, los datos
  cambiaron" y menor énfasis visual) hasta el próximo cálculo, para que no
  parezca corresponder a las entradas actuales.

### 4.9 Restablecer

- Limpia errores y resultado, y repone los valores iniciales acordados
  (Parcial 1 / 3.5 / 30; Parcial 2 / 2.5 / 30; Proyecto / 4.0 / 40).

## 5. Plan breve de implementación

Archivos (única carpeta nueva del frente):

- `web/index.html`: estructura semántica de la pantalla.
- `web/styles.css`: estilos, diseño adaptable y estados visuales.
- `web/app.js`: lógica de interfaz y consumo de la API.

Decisiones técnicas:

1. Sin framework ni dependencias nuevas; HTML, CSS y JavaScript planos.
2. Constantes centralizadas en un único objeto de configuración al inicio de
   `app.js`: URL del endpoint (`/api/v1/calcular`, relativa), valores iniciales,
   límites (nota 0–5 en pasos de 0.1, peso entero 0–100, nombre 1–80 caracteres)
   y textos de presentación.
3. Conversión de entradas a números JSON estricta: un campo vacío no se
   convierte en cero; se reporta como dato faltante. No se envían claves
   adicionales. Aun con peso 0 se exige la nota.
4. El servidor es la autoridad del cálculo: la interfaz no implementa un segundo
   motor de definitiva ni un estado académico local alternativo.
5. Accesibilidad: etiquetas `<label>` explícitas por campo, navegación completa
   por teclado, foco visible, contraste AA, errores anunciados por texto y
   regiones `aria-live` para resultado y resumen de errores.
6. Los nombres y mensajes se insertan como texto (`textContent`), nunca como
   HTML; no se guarda nada en almacenamiento del navegador.
7. Consumo con `fetch` y URL relativa, mismo origen; sin CORS adicional.
8. Puesta en marcha: al crear `web/` por primera vez se reinicia el servidor
   para registrar `/static` (limitación documentada en `docs/backend.md`).

Verificación posterior (a registrar en `docs/pruebas_interfaz.md` cuando la
interfaz exista): ejemplo del contrato 3.4/APROBADO, pesos que suman 110, nota
5.1, campos vacíos, redondeo 2.95 → 3.0, restablecer, navegación por teclado,
móvil, error de servidor y desconexión.

## 6. Aprobación

- [ ] Maqueta de escritorio aprobada por Jose.
- [ ] Maqueta de móvil aprobada por Jose.
- [ ] Estados (4.1 a 4.9) aprobados por Jose.

Comentarios de aprobación: _(pendiente)_
