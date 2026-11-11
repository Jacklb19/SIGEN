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
| Puerta de calidad (líneas ≥ 80 %, ramas informadas) | Implementada: 255 pruebas, líneas 203/203, ramas 50/50 | Stefven |
| Ruff y Bandit | Sin hallazgos en la puerta; hallazgos ampliados registrados | Stefven |
| Carga con Locust (10/20/50 usuarios) | Medida localmente | Stefven |
| GitHub Actions | **Workflow preparado y comandos verificados localmente; ejecución remota pendiente** de publicar con autorización | Stefven |
| Docker y RF-09 (nota necesaria) | Fuera del primer alcance | — |

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

## Tecnologías

Python 3.11, FastAPI, Uvicorn, Pydantic, Pytest, pytest-cov, httpx2, jsonschema, Ruff, Bandit, Locust y GitHub Actions. HTML, CSS y JavaScript sin frameworks para la interfaz. Versiones exactas en `requirements.txt` y `requirements-dev.txt`.

## Instalación (PowerShell, desde la raíz del repositorio)

Requiere Python 3.11.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pip install --no-deps -e .
python -m pip check
```

Si `py -3.11` no está disponible, crear el entorno con cualquier intérprete 3.11 (por ejemplo, `C:\ruta\python3.11\python.exe -m venv .venv`). La instalación editable es la prevista: el servidor localiza `web/` relativo al código fuente. No hace falta `PYTHONPATH`.

En Linux/macOS: `python3.11 -m venv .venv` y `source .venv/bin/activate`; el resto de comandos es igual.

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
```

`verificar_calidad.py` ejecuta Pytest con cobertura de `sigen` (líneas y ramas, reportes en consola, `htmlcov/` y `coverage.json`), propaga cualquier fallo y exige `covered_lines / num_statements >= 0.80`. Falla si el reporte falta, está mal formado o no tiene sentencias. Las ramas se informan aparte, sin umbral (no hay uno acordado). La CI ejecuta exactamente estos comandos.

Subconjuntos útiles:

```powershell
python -m pytest tests/unit tests/api     # pruebas de Jose
python -m pytest tests/contract           # contrato independiente
```

Para comprobar el contrato contra un servidor real ya arrancado:

```powershell
$env:SIGEN_URL_BASE = 'http://127.0.0.1:8000'
python -m pytest tests/contract
Remove-Item Env:SIGEN_URL_BASE
```

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

- La ejecución de CI en GitHub no se ha comprobado (requiere publicar con autorización).
- Las mediciones de carga son locales, con generador y servidor en el mismo equipo, y no fijan ni prometen un SLO.
- Docker y RF-09 quedan fuera del primer alcance; confirmar con la rúbrica si son exigibles.

## Equipo

| Integrante | Frente |
|---|---|
| Jose | Motor, validaciones y API |
| Santiago | Interfaz y accesibilidad |
| Stefven | Configuración, contrato independiente, calidad, carga y evidencias |

Cualquier cambio de rutas, códigos, tipos o reglas del contrato se coordina entre los tres y actualiza contrato, backend, interfaz y pruebas a la vez.
