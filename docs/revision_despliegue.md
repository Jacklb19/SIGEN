# Revisión integrada y preparación para despliegue

## Cierre del 11 de noviembre de 2026

- `src/app.py` expone FastAPI para Vercel y `.python-version` selecciona Python 3.12.
- En Python 3.12.14 aprobaron 255 pruebas. El contrato con Requests contra Uvicorn aprobó 118.
- Las tres regresiones de interfaz aprobaron tras corregir precisión y foco.
- El wheel incluyó los recursos y respondió 200 en `/`, `/static/app.js`, `/static/styles.css` y `/health`.
- Se añadió Docker, observabilidad básica y la configuración de SonarQube Cloud. Sonar requiere la activación del proyecto y su token.
- La [guía de Vercel](despliegue_vercel.md) describe la publicación y la comprobación posterior.

Los apartados siguientes conservan el diagnóstico y la evidencia de la revisión inicial.

Fecha: 11 de noviembre de 2026. Objetivo indicado por Jose: servicio gratuito, preferiblemente Vercel. Esta revisión no despliega, crea cuentas ni publica cambios.

## Dictamen

La aplicación integrada funciona como demostración desde el código fuente y supera las comprobaciones de backend y calidad. **No se considera todavía lista para importar y desplegar en Vercel sin preparación adicional.** Hay trabajo de configuración del destino y dos defectos reproducidos en la interfaz. Un verde de CI en Python 3.11 no sustituye probar el runtime, el artefacto y las rutas que realmente se usarán al desplegar.

## Trabajo remoto traído

Solo hay un remoto configurado, `origin`, en `https://github.com/Jacklb19/SIGEN.git`. Se consultaron todas sus ramas:

| Referencia remota | Commit revisado | Estado |
|---|---|---|
| origin/main | a134c45 | Backend e interfaz de Santiago; PR #1 ya integrado. |
| origin/santiago/interfaz | e41d92d | Incluido en main y en la rama de calidad. |
| origin/stefven/calidad | 5d175f4 | Contiene todo lo anterior más dependencias, pruebas, CI y evidencias. |

La carpeta local se actualizó de 1a3a102 a 5d175f4 por avance directo. No se creó un commit de merge ni se reescribió autoría. `main` local queda 11 commits por delante de `origin/main`. Eso no significa que GitHub main ya incluya la calidad: la publicación o integración remota sigue pendiente. No se hizo push en esta revisión.

Se conservó el historial remoto de cada compañero; no se reasignó a Jose la autoría de commits existentes. No se crearon commits nuevos durante la revisión.

## Comprobaciones ejecutadas

Se creó un entorno aislado en `.venv/revision`, con Python 3.11.16, se instalaron `requirements.txt` y `requirements-dev.txt` y el paquete editable, y se ejecutó pip check: sin dependencias incompatibles.

| Comprobación | Resultado nuevo de esta revisión |
|---|---|
| python scripts/verificar_calidad.py | 255 pruebas aprobadas, sin advertencias. |
| Líneas del paquete sigen | 203/203, 100 %. |
| Ramas del paquete sigen | 50/50, 100 %. |
| Ruff check y format | Aprobados; 30 archivos Python con formato correcto. |
| Bandit sobre src | Sin hallazgos con la configuración del proyecto. |
| Contrato contra Uvicorn real en localhost | 118 pruebas aprobadas. |
| Navegador contra el servidor real | Ejemplo 3.4/APROBADO; rechazo de 3.55; suma 110 con mensaje; restablecer; 2.95 → 3.0/APROBADO. |
| CI remota consultada con GitHub CLI | Run 42963314108, commit 5d175f4, completed/success en stefven/calidad. |
| Construcción de wheel no editable | Construye, pero no contiene HTML, CSS ni JavaScript; ver hallazgo de empaquetado. |
| Búsqueda de patrones comunes de secretos | Sin coincidencias; no equivale a una auditoría exhaustiva. |

La CI remota puede verificarse en [GitHub Actions](https://github.com/Jacklb19/SIGEN/actions/runs/42963314108). Las cifras históricas de Locust del equipo se revisaron en sus CSV y reporte, pero no se repitieron cargas en esta sesión ni se extrapolaron a Vercel. Los servidores locales temporales de esta revisión se detuvieron al terminar; no se terminaron procesos ajenos.

## Pendientes antes de Vercel

### 1. Falta la entrada reconocida por Vercel

La aplicación está en `src/sigen/api.py`, pero no hay entrada convencional como `app.py` o `src/app.py`, ni `tool.vercel.entrypoint`. La guía oficial admite esas entradas o un módulo personalizado configurado. Preparar una entrada compatible con el layout src y probar el build; no basta con que Uvicorn importe el paquete tras instalarlo editable.

Ubicaciones relevantes: `pyproject.toml`, `src/sigen/api.py`. Es un bloqueo de preparación del destino, no un fallo del contrato académico.

### 2. Falta probar y fijar el runtime del destino

Las comprobaciones integradas y CI están en Python 3.11. La documentación de Vercel consultada enumera 3.12 por defecto, 3.13 y 3.14. `requires-python >=3.11` permite versiones más nuevas, pero no selecciona una versión comprobada para Vercel. Preparar un runtime soportado, verificar dependencias y ejecutar la suite en él antes de certificar el despliegue. La diferencia no demuestra que el código falle en 3.12; demuestra que falta esa verificación.

### 3. Los recursos web dependen de la instalación editable

`src/sigen/config.py` resuelve `web/` mediante la ubicación del módulo. El wheel generado no incluye `web/`. Al importar una copia extraída de ese wheel, el resultado fue `/health` 200, `/` 404 y `/static/app.js` 404. El resultado se obtuvo sin modificar el código de los compañeros.

Para desplegar desde código fuente, asegurar y comprobar que el build conserva `web/` y que la ruta resuelta apunta al lugar correcto. Si se distribuye como wheel, incluir los recursos y resolverlos desde el paquete. Vercel tiene reglas propias de bundle y montaje de estáticos: el fallo del wheel no demuestra por sí solo que un bundle de Vercel falle, pero impide tratar ambas instalaciones como equivalentes. No elegir una solución sin verificar el artefacto real.

### 4. Elegir la revisión remota que se desplegará

GitHub main todavía no tiene los 11 commits de Stefven. Integrarlos de forma coordinada o seleccionar expresamente la rama de calidad para una primera revisión de despliegue. Después verificar la CI de la revisión elegida. No hacer force-push ni reescribir commits para resolver esto.

## Defectos reproducidos en la interfaz

### Precisión de entrada alterada por conversión a Number

En `web/app.js:163`, una nota se convierte a Number antes de verificar su precisión. En el navegador, `3.5000000000000000000000000001` se aceptó y terminó como un cálculo exitoso 3.4/APROBADO. La API, si recibe el token original, lo rechaza correctamente. El navegador ya lo había redondeado a 3.5 y el servidor no puede recuperar lo escrito.

Corrección sugerida: validar el valor decimal escrito antes de convertirlo, permitiendo ceros finales conforme al contrato y rechazando precisión no admitida. No usar una tolerancia binaria como sustituto de esa regla. Añadir un caso de regresión de interfaz.

### El foco se intenta mover mientras los campos siguen deshabilitados

En `web/app.js:288` se intenta enfocar el campo con error, pero la respuesta se procesa con los controles deshabilitados y solo se habilitan en el finally de `calcular`. Se reprodujo usando `3.50000000001`: el servidor devolvió PRECISION, apareció el mensaje y los controles se habilitaron, pero el foco quedó en BODY, no en nota-0.

Corrección sugerida: restaurar los controles antes de enfocar el campo o ejecutar el movimiento de foco después del finally. El resumen general también necesita ser enfocable si se usa como destino de foco.

Estos defectos no afectan la exactitud del motor cuando recibe datos válidos, pero contradicen reglas de validación y accesibilidad de la interfaz. Los 255 tests actuales no comprueban estos flujos de navegador; la cobertura del backend no cubre JavaScript.

## Observaciones de entrega

- Hay 15 archivos `.tmp` vacíos dentro de `docs/evidencias/carga/corrida-1`. No son un bloqueo funcional, pero conviene retirarlos del material de entrega conservando los CSV y las evidencias reales. No se borraron durante la revisión.
- La documentación histórica del backend menciona pendientes que ya completó Stefven. README y reporte de calidad describen el estado integrado más reciente; actualizar los textos históricos al cerrar la integración para evitar confusión.
- No se verificaron otra vez móvil, Safari, Firefox ni lectores de pantalla. Tampoco se probó un despliegue público, una cuenta Vercel ni cuotas consumidas.

## Camino previsto sin gasto

Vercel ofrece un plan Hobby gratuito para proyectos personales, sujeto a sus condiciones y cuotas. El simulador académico sin base de datos puede evaluarse en un único proyecto FastAPI con la interfaz en el mismo origen, evitando separar frontend/backend y añadir CORS sin necesidad. Esta es una propuesta de arquitectura, no un despliegue confirmado ni una garantía de cuota suficiente.

Antes de publicar: preparar entrada/runtime/estáticos, corregir las dos incidencias de interfaz, repetir las comprobaciones afectadas y revisar el build del destino. Después avisar a Jose para autorizar el despliegue y validar en la URL pública `/`, recursos estáticos, `/health`, cálculo y errores. No activar planes de pago ni contratar dominio.

## Referencias oficiales consultadas

- [FastAPI en Vercel: entradas y estáticos](https://vercel.com/docs/frameworks/backend/fastapi).
- [Runtime Python de Vercel: versiones y bundle](https://vercel.com/docs/functions/runtimes/python).
- [Plan Hobby](https://vercel.com/docs/plans/hobby).
- [Setuptools: recursos de un paquete distribuible](https://setuptools.pypa.io/en/latest/userguide/datafiles.html).
