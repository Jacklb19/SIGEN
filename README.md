# SIGEN Lite

Sistema de Gestión y Evaluación de Notas Universitarias: prototipo académico para la asignatura **Pruebas y Mantenimiento de Software**.

**Problema:** errores de captura, validación o cálculo de notas pueden pasar inadvertidos si el sistema solo se prueba con entradas comunes. SIGEN Lite valida tres actividades evaluativas, calcula una definitiva ponderada y sirve de caso para demostrar pruebas funcionales, de integración, de contrato, cobertura, análisis estático, carga y mantenimiento.

Es un simulador con datos ficticios, sin cuentas, base de datos ni integración institucional.

## Estado

| Componente | Estado | Responsable |
|---|---|---|
| Motor Decimal, validaciones y API FastAPI | Implementado | Jose |
| Interfaz web (`/`) | Implementada con maqueta aprobada | Santiago |
| Paquete instalable y dependencias fijadas | Implementado | Stefven |
| Pruebas independientes de contrato (118) | Implementadas y aprobadas localmente | Stefven |
| Puerta de calidad (líneas ≥ 80 %, ramas informadas) | 255 pruebas Python y 3 regresiones de interfaz | Equipo |
| Ruff y Bandit | Sin hallazgos en la puerta; hallazgos ampliados registrados | Stefven |
| Carga con Locust (10/20/50 usuarios) | Medida localmente | Stefven |
| GitHub Actions | Python 3.12, regresiones de interfaz y verificación de Docker | Equipo |
| Docker | Imagen de aplicación y etapa de pruebas | Equipo |
| SonarQube Cloud | Configuración en CI, activación con credenciales del proyecto | Jose |

## Documentación

- [Guía completa: requisitos, contrato, arquitectura y plan](SIGEN_Lite_Guia_Completa.md)
- [Requisitos y alcance del backend](docs/requisitos.md)
- [Contrato de la API](docs/contrato_api.md)
- [Backend: organización y notas de Jose](docs/backend.md)
- [Interfaz](docs/interfaz.md), [maqueta](docs/maqueta_interfaz.md) y [pruebas de interfaz](docs/pruebas_interfaz.md)
- [Matriz de pruebas (RF, riesgos, TP, evidencias)](docs/matriz_pruebas.md)
- [Reporte de calidad: cobertura, análisis estático, CI y carga](docs/reporte_calidad.md)
- [Mantenimiento correctivo y regresión](docs/mantenimiento.md)
- [Evidencias](docs/evidencias/)
- [Guion de sustentación y lista de entrega](docs/sustentacion.md)
- [Despliegue en Vercel](docs/despliegue_vercel.md)

## Tecnologías

Python 3.12, FastAPI, Uvicorn, Pydantic, Pytest, pytest-cov, Requests, httpx2, JSON Schema, Ruff, Bandit, Locust, Docker y GitHub Actions. La interfaz usa HTML, CSS y JavaScript. Node.js ejecuta sus pruebas de regresión. Versiones de Python y dependencias en `.python-version` y `requirements*.txt`.

## Instalación (PowerShell, desde la raíz del repositorio)

Usar Python 3.12, igual que en CI y Vercel.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pip install --no-deps -e .
python -m pip check
```

El paquete incluye los archivos de interfaz en `src/sigen/web/` y funciona con instalación editable o mediante wheel.

En Linux y macOS, crear el entorno con `python3.12 -m venv .venv` y activarlo con `source .venv/bin/activate`.

## Ejecutar la aplicación

```powershell
python -m uvicorn sigen.api:app --reload
```

- Interfaz: <http://127.0.0.1:8000/>
- Documentación interactiva: <http://127.0.0.1:8000/docs>
- Salud: `GET /health` · Cálculo: `POST /api/v1/calcular`

`--reload` es solo para desarrollo; para medir carga usar `--workers 1` sin reload.

## Pruebas y calidad

```powershell
python scripts/verificar_calidad.py           # suite completa + cobertura + puerta de líneas
python -m ruff check .                        # estilo y posibles defectos
python -m ruff format --check .               # formato
python -m bandit -c pyproject.toml -r src -q  # patrones de seguridad en el código productivo
node --test tests/ui/test_interfaz.cjs        # regresiones del formulario
```

`verificar_calidad.py` ejecuta Pytest con cobertura de `sigen` (líneas y ramas, reportes en consola, `htmlcov/` y `coverage.json`), propaga cualquier fallo y exige `covered_lines / num_statements >= 0.80`. Falla si el reporte falta, está mal formado o no tiene sentencias. Las ramas se informan aparte, sin umbral (no hay uno acordado). La CI ejecuta exactamente estos comandos.

Subconjuntos útiles:

```powershell
python -m pytest tests/unit tests/api     # pruebas de Jose
python -m pytest tests/contract           # contrato independiente
```

Para comprobar el contrato con Requests contra un servidor real ya arrancado:

```powershell
$env:SIGEN_URL_BASE = 'http://127.0.0.1:8000'
python -m pytest tests/contract
Remove-Item Env:SIGEN_URL_BASE
```

## Docker

```powershell
docker build -t sigen:local .
docker run --rm -p 127.0.0.1:8000:8000 sigen:local
```

La aplicación se abre en <http://127.0.0.1:8000/>. Para ejecutar la suite Python dentro del contenedor:

```powershell
docker build --target pruebas -t sigen:pruebas .
docker run --rm sigen:pruebas
```

## SonarQube Cloud y observabilidad

En SonarQube Cloud, importar el repositorio público y elegir análisis por CI. En GitHub, configurar las variables `SONAR_ORGANIZATION` y `SONAR_PROJECT_KEY` y guardar el token como secreto `SONAR_TOKEN`. El paso de análisis se habilita en los pushes a `main` al configurar ambas variables. La puerta genera `coverage.xml` para el análisis. La activación requiere los datos del proyecto en SonarQube Cloud.

En ejecución con Uvicorn, la API registra método, ruta, estado HTTP y tiempo en milisegundos. Las respuestas procesadas incluyen `Server-Timing`.

## Pruebas de carga

En dos terminales (con el entorno activado):

```powershell
python -m uvicorn sigen.api:app --host 127.0.0.1 --port 8000 --workers 1
python -m locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 10 -r 5 -t 60s --csv docs/evidencias/carga/u10
```

Repetir con `-u 20` y `-u 50`. Sin `--headless`, Locust abre su panel en <http://localhost:8089>. Mezcla objetivo 70 % cálculo válido, 20 % salud y 10 % inválidos esperados; cada respuesta se valida por código y cuerpo. Resultados y condiciones en el [reporte de calidad](docs/reporte_calidad.md#6-pruebas-de-carga).

## Reglas y política de redondeo

- Exactamente tres actividades; nombre de 1–80 caracteres tras recortar.
- Nota: número JSON finito de 0.0 a 5.0, múltiplo de 0.1 (se aceptan `3`, `3.50`, `35e-1`); sin cadenas, booleanos ni `null`.
- Peso: entero JSON de 0 a 100 (`30.0` se rechaza); los tres suman 100.
- Cálculo con `Decimal`, sin redondeos intermedios. **Política asumida del prototipo, no regla institucional certificada:** la definitiva es el promedio redondeado a un decimal con `ROUND_HALF_UP`; `APROBADO` si la definitiva es ≥ 3.0. Ejemplo: 3.5/2.5/4.0 con 30/30/40 → 3.4 `APROBADO`; un promedio de 2.95 da definitiva 3.0 `APROBADO`. Debe validarse con el docente antes de cualquier uso real.

## Límites conocidos

- Las mediciones de carga son locales, con generador y servidor en el mismo equipo, y no fijan ni prometen un SLO.
- RF-09 (nota necesaria) e IaC dependen de la rúbrica del profesor.

## Equipo

| Integrante | Frente |
|---|---|
| Jose | Motor, validaciones y API |
| Santiago | Interfaz y accesibilidad |
| Stefven | Configuración, contrato independiente, calidad, carga y evidencias |

Cualquier cambio de rutas, códigos, tipos o reglas del contrato se coordina entre los tres y actualiza contrato, backend, interfaz y pruebas a la vez.
