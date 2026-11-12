# Interfaz de SIGEN Lite

Documentación de comportamiento del frente de interfaz (Santiago). Implementa
la maqueta aprobada en `docs/maqueta_interfaz.md` y consume la API descrita en
`docs/contrato_api.md`. No modifica backend, pruebas ni configuración.

## Archivos

- `src/sigen/web/index.html`: estructura semántica de la pantalla única, en español.
- `src/sigen/web/styles.css`: estilos, diseño adaptable (punto de corte 768 px) y
  estados visuales (error, éxito, desactualizado, carga).
- `src/sigen/web/app.js`: validación de entradas, consumo de la API y representación de
  resultados y errores. Sin dependencias ni framework.

El backend sirve `index.html` en `/` y expone los recursos empaquetados bajo `/static`.

## Pantalla

La rama `mejoras/interfaz-simulacion` añade el nombre opcional de la materia, una barra que indica cuánto falta o sobra para llegar al 100 % y un resultado que destaca la definitiva. El nombre de la materia se muestra en el resultado y se limpia con **Restablecer**. El JSON conserva únicamente las tres actividades.

- Tres actividades con nombre, nota y peso. Valores iniciales: Parcial 1
  (3.5, 30), Parcial 2 (2.5, 30) y Proyecto (4.0, 40).
- Total de pesos visible, recalculado al editar; es solo informativo.
- Botones Calcular definitiva y Restablecer.
- Resultado con promedio ponderado, definitiva con exactamente un decimal y
  estado APROBADO/REPROBADO, más la aclaración de que el redondeo es una
  política del simulador y no una regla institucional certificada.
- Escritorio (≥ 768 px): filas de tres columnas con encabezados; las etiquetas
  quedan accesibles para lectores de pantalla aunque se ocultan visualmente.
- Móvil (< 768 px): una tarjeta apilada por actividad con etiquetas visibles,
  campos y botones de al menos 44 px de alto.

## Configuración centralizada

`app.js` concentra en el objeto `CONFIG` la ruta del endpoint
(`/api/v1/calcular`, relativa al mismo origen), los valores iniciales, los
límites del contrato (nota 0–5 en pasos de 0.1, peso entero 0–100, nombre
1–80 caracteres tras recortar) y los textos de presentación.

## Validación de entradas y alcance

- Un campo vacío nunca se convierte en cero: se reporta como obligatorio.
- La nota exige formato decimal, rango 0–5 y múltiplos de 0.1. La precisión se
  valida antes de convertir el texto y se admiten ceros finales. También se
  requiere la nota cuando el peso es cero.
- El peso exige dígitos enteros (se rechazan `30.0`, decimales y notación
  exponencial) en rango 0–100.
- El nombre se recorta en los extremos y exige 1–80 caracteres.
- La carga JSON envía únicamente `actividades` con `nombre`, `nota` y `peso`;
  sin claves adicionales.
- La suma de pesos **no** se valida en el cliente: es una regla global del
  servidor (`PONDERACION_INVALIDA`, 400) y la interfaz la presenta junto al
  total de pesos cuando llega. El servidor es la autoridad del cálculo; la
  interfaz no implementa un segundo motor de definitiva ni un estado académico
  local alternativo.

## Errores

- **422 VALIDACION**: cada entrada de `error.campos` se ubica por su ruta
  (`actividades.<índice>.<campo>`, índice desde cero) bajo el campo
  correspondiente, con `aria-invalid` y `aria-describedby`; el foco se mueve al
  primer campo con error después de habilitarlo. Rutas no reconocibles (p. ej. `body`) se listan en el
  resumen general. No se depende del orden ni del texto literal.
- **400 PONDERACION_INVALIDA**: el mensaje de la ruta `actividades.pesos` se
  muestra junto al total de pesos, además del resumen general.
- **500 ERROR_INTERNO**: mensaje genérico sin trazas técnicas.
- **Conexión fallida o respuesta inesperada**: mensaje de conexión genérico;
  una respuesta 200 con forma distinta al contrato se trata como respuesta
  inesperada.

## Estados de la interacción

- Durante el cálculo los campos y botones se deshabilitan y el botón indica
  "Calculando…" con `aria-busy`; los controles se restauran en éxito y en
  fallo, y se evitan envíos duplicados.
- Si los datos cambian después de un cálculo, el resultado se marca como
  desactualizado (borde punteado, menor énfasis y aviso en texto) hasta el
  próximo cálculo exitoso.
- Restablecer limpia errores y resultado, repone los valores iniciales y
  devuelve el foco al primer campo.
- Nombres y mensajes se insertan con `textContent` (nunca HTML) y no se guarda
  nada en el almacenamiento del navegador.

## Ejecución local

Con el entorno del proyecto (ver `docs/backend.md`):

```powershell
python -m uvicorn sigen.api:app
```

Abrir `http://localhost:8000/`.

Las verificaciones realizadas se registran en `docs/pruebas_interfaz.md`.
