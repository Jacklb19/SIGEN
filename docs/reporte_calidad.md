# Reporte de calidad de SIGEN Lite

Frente de Stefven: configuración reproducible, puerta de cobertura, análisis estático, CI y carga. Todas las cifras de este documento se obtuvieron realmente el 10 de noviembre de 2026 (hora de Colombia; las evidencias usan UTC, 11-nov 04:4x–04:5x) en la rama `stefven/calidad`. No constituyen un SLO ni garantizan ausencia de defectos.

## 1. Entorno de medición

| Elemento | Valor |
|---|---|
| SO | Windows 11 Home Single Language 10.0.26300 |
| CPU | Intel Core Ultra 9 185H (16 núcleos, 22 hilos) |
| RAM | 31,4 GB |
| Python | 3.11.18 (conda-forge) en `.venv` durante las mediciones; después se instaló Python 3.11.9 (python.org) y la puerta se repitió con el mismo resultado (255 aprobadas, 203/203 líneas, 50/50 ramas) |
| Dependencias | Las de `requirements.txt` y `requirements-dev.txt` (FastAPI 0.162.4, Starlette 1.10.0, Uvicorn 0.54.0, Pydantic 2.14.3, pytest 9.2.0, pytest-cov 7.1.0, coverage 7.17.2, httpx2 2.16.0, jsonschema 4.26.0, Ruff 0.17.4, Bandit 1.9.4, Locust 2.47.0) |

## 2. Dependencias y advertencia Starlette/httpx

Con `httpx 0.28.1`, Starlette 1.10 emite `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead`. Se evaluó la alternativa: con `httpx2 2.16.0` y sin `httpx`, las 119 pruebas de Jose pasaron incluso con `-W error::DeprecationWarning`, sin cambiar su código (siguen importando `fastapi.testclient`). Decisión: `httpx2` sustituye a `httpx` en desarrollo y Pytest se configura con `filterwarnings = ["error"]`, de modo que una deprecación futura haga fallar la suite en vez de pasar inadvertida.

Los rangos compatibles viven en `pyproject.toml`; los archivos `requirements*.txt` son locks generados con `uv pip compile --universal` para Python 3.11 (incluyen marcadores como `pywin32 ; sys_platform == 'win32'`, imprescindible para que la CI en Linux no falle). Ver [mantenimiento.md](mantenimiento.md#actualizar-dependencias).

## 3. Pruebas y cobertura

Comando: `python scripts/verificar_calidad.py` — [salida completa](evidencias/calidad/puerta_calidad.txt).

| Suite | Responsable | Pruebas |
|---|---|---:|
| `tests/unit` | Jose | 49 |
| `tests/api` | Jose | 70 |
| `tests/contract` | Stefven | 118 |
| `tests/calidad` | Stefven | 18 |
| **Total** | | **255 aprobadas, 0 fallidas** |

| Métrica (paquete `sigen`) | Resultado | Criterio |
|---|---|---|
| Líneas (`covered_lines / num_statements`) | 203 / 203 = 100 % | ≥ 80 % (RNF-04) — **cumple** |
| Ramas (`covered_branches / num_branches`) | 50 / 50 = 100 % | Informativo; no hay umbral acordado |

Ningún archivo productivo se excluyó. Un 100 % de cobertura solo indica que todo el código se ejecutó; la demostración de mantenimiento muestra además que las pruebas **detectan** un defecto de frontera (6 fallos ante `nota < 5.0`).

La puerta no usa `--cov-fail-under`: con `--cov-branch` ese porcentaje combina líneas y ramas. `tests/calidad/test_verificar_calidad.py` prueba que un 79 % de líneas con 100 % de ramas (combinado 86 %) **falla**, igual que un reporte ausente, mal formado, con 0 sentencias o heredado de una ejecución anterior.

## 4. Análisis estático

Ruff analiza estilo y posibles defectos; **no es un escáner de seguridad**. Bandit busca patrones de seguridad conocidos en Python; tampoco sustituye una revisión de seguridad completa. SonarQube Cloud no se conectó (requiere autorización y cuenta).

### Comandos de la puerta (los mismos que en CI)

| Herramienta | Versión | Comando | Resultado |
|---|---|---|---|
| Ruff | 0.17.4 | `python -m ruff check .` | Sin hallazgos |
| Ruff | 0.17.4 | `python -m ruff format --check .` | Todos los archivos Python con formato correcto |
| Bandit | 1.9.4 | `python -m bandit -c pyproject.toml -r src -q` | Sin hallazgos |

Reglas Ruff activas: `E, F, W, I, B, UP, SIM, C4, RUF` (antes solo se usaban las predeterminadas), con `UP042` ignorada (ver tabla). Evidencias: [ruff.txt](evidencias/calidad/ruff.txt), [bandit.txt](evidencias/calidad/bandit.txt).

### Hallazgos reales y decisiones

Además de la puerta, se ejecutó una exploración ampliada con reglas `N` (nombres) y `PT` (estilo pytest), y Bandit sobre los archivos de Stefven. Todos los hallazgos siguientes son reales; no hay otros.

| Herramienta / regla | Archivo:línea | Severidad | Explicación | Decisión |
|---|---|---|---|---|
| Ruff N818 | `scripts/verificar_calidad.py:48` | Estilo | Excepción `ReporteInvalido` sin sufijo `Error`. | **Corregido**: `ReporteInvalidoError` (commit `refactor(calidad)…`). Antes/después en `ruff.txt`. |
| Ruff UP042 | `src/sigen/domain.py:8` | Mantenibilidad | `Estado(str, Enum)` podría ser `StrEnum`. | **Pendiente, reportado a Jose.** `StrEnum` cambia `str(Estado.APROBADO)` (de `Estado.APROBADO` a `APROBADO`); no es un cambio cosmético y el archivo es de su frente. Se ignora en la puerta para no bloquear la CI con una decisión ajena. |
| Ruff N818 | `src/sigen/domain.py:35` | Estilo | `DatosInvalidos` sin sufijo `Error`. | **Pendiente, reportado a Jose.** Renombrar afecta a toda la API del dominio y sus pruebas. Fuera de la puerta (regla `N` no activa). |
| Ruff PT006 (×7) | `tests/api/test_api.py:66,110,208,252`; `tests/unit/test_calculator.py:32,100,115` | Estilo | `parametrize` recibe nombres como cadena y no como tupla. | **Pendiente, reportado a Jose.** Sin impacto funcional; fuera de la puerta. |
| Bandit B311 (×2) | `locustfile.py:98,146` | Baja / confianza alta | `random.choice` no es apto para criptografía. | **Falso positivo justificado:** solo elige el caso de carga a enviar; no hay uso de seguridad. |
| Bandit B404 | `scripts/verificar_calidad.py:21` | Baja | Importa `subprocess`. | **Falso positivo justificado:** necesario para ejecutar Pytest. |
| Bandit B603 | `scripts/verificar_calidad.py:117` | Baja | `subprocess.run` sin shell. | **Falso positivo justificado:** lista fija de argumentos con `sys.executable`; ninguna entrada externa. |

`src/sigen` no tiene hallazgos de Bandit. Ningún hallazgo de Ruff es una vulnerabilidad.

## 5. Integración continua

`.github/workflows/ci.yml`: en cada push y pull request, Ubuntu + Python 3.11, instalación desde los locks, `pip check`, Ruff (lint y formato), Bandit sobre `src` y `python scripts/verificar_calidad.py`; sube `coverage.json` y `htmlcov/` como artefacto. Cualquier paso con código distinto de cero hace fallar el job.

| Estado | |
|---|---|
| Workflow preparado | **Sí** |
| Comandos verificados localmente | **Sí** (Windows, mismos comandos y locks; YAML validado sintácticamente) |
| Ejecución remota comprobada | **Sí.** Push autorizado de `stefven/calidad` el 11-nov-2026; workflow `CI` sobre el commit `9d9a095`, conclusión `success` ([run](https://github.com/Jacklb19/SIGEN/actions/runs/42962657637)). |

## 6. Pruebas de carga

### Configuración

| Parámetro | Valor |
|---|---|
| Servidor | `python -m uvicorn sigen.api:app --host 127.0.0.1 --port 8000 --workers 1` (sin `--reload`, `--log-level warning`) |
| Generador | `python -m locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u N -r 5 -t 60s --csv docs/evidencias/carga/uN --only-summary` |
| Perfiles | 10, 20 y 50 usuarios; incremento 5 usuarios/s; 60 s cada uno; ejecutados consecutivamente |
| Espera entre tareas | `between(0.5, 1.5)` s por usuario |
| Calentamiento | Ninguno específico. Antes de la corrida 1, el mismo servidor atendió las 118 pruebas de contrato |
| Mezcla objetivo | 70 % cálculo válido (4 casos con resultado esperado), 20 % salud, 10 % inválidos esperados (nota 5.1 → 422 RANGO, suma 110 → 400 SUMA_PESOS, JSON roto → 422 JSON_INVALIDO) |
| Validación | `catch_response`: se comprueba HTTP, Content-Type y cuerpo; un 400/422 solo es éxito si coincide con el error esperado |
| Ubicación | **Servidor y Locust comparten el mismo equipo** (compiten por CPU). No se midió consumo de recursos |

### Resultados de la corrida 2 (vigente)

Evidencia: `docs/evidencias/carga/u{10,20,50}_stats.csv`, `_stats_history.csv`, `_failures.csv` y `_consola.txt`. Tiempos en milisegundos.

| Usuarios | Escenario | Solicitudes | RPS | Promedio | Mediana | p95 | Máx | Fallos |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 10 | calcular válido | 425 | 7,15 | 7,99 | 3 | 24 | 290 | 0 |
| 10 | salud | 104 | 1,75 | 3,50 | 2 | 16 | 20 | 0 |
| 10 | inválidos esperados (3) | 57 | 0,96 | 2,8–4,1 | 3 | 4–12 | 12 | 0 |
| 10 | **Agregado** | **586** | **9,86** | **6,75** | **3** | **19** | **290** | **0 (0 %)** |
| 20 | calcular válido | 763 | 12,86 | 33,66 | 3 | 21 | 3 362 | 0 |
| 20 | salud | 200 | 3,37 | 58,46 | 3 | 31 | 3 361 | 0 |
| 20 | inválidos esperados (3) | 113 | 1,90 | 3,4–16,3 | 3 | 4–13 | 528 | 0 |
| 20 | **Agregado** | **1 076** | **18,14** | **35,64** | **3** | **21** | **3 362** | **0 (0 %)** |
| 50 | calcular válido | 1 854 | 30,90 | 6,82 | 3 | 21 | 651 | 0 |
| 50 | salud | 582 | 9,70 | 6,27 | 3 | 19 | 128 | 0 |
| 50 | inválidos esperados (3) | 275 | 4,58 | 4,7–6,8 | 3–4 | 12–27 | 75 | 0 |
| 50 | **Agregado** | **2 711** | **45,18** | **6,57** | **3** | **20** | **651** | **0 (0 %)** |

Mezcla observada (corrida 2, 10 usuarios): 72,5 % cálculo, 17,7 % salud, 9,7 % inválidos; en todos los perfiles queda cerca del 70/20/10 objetivo.

### Corrida 1 (conservada)

Evidencia en [evidencias/carga/corrida-1/](evidencias/carga/corrida-1/). Mismos parámetros; el locustfile solo difería en los nombres de escenario (con tildes) y en el texto de diagnóstico de fallos.

| Usuarios | Solicitudes | RPS | Promedio | Mediana | p95 | Máx | Fallos |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 578 | 9,84 | 4 | 3 | 11 | 270 | 0 |
| 20 | 1 057 | 17,83 | 48 | 3 | 30 | 5 357 | **7 (0,66 %)** |
| 50 | 2 677 | 44,94 | 11 | 4 | 29 | 503 | 0 |

Los 7 fallos (5 de cálculo, 2 de salud) fueron respuestas **HTTP 0** (sin respuesta) en un mismo segundo (04:40:50Z). La versión de entonces no registraba la excepción de conexión; por eso se añadió ese diagnóstico antes de la corrida 2.

### Análisis

- La mediana se mantuvo en 3–4 ms en todos los perfiles y el throughput creció de forma aproximadamente proporcional a los usuarios (≈10 → 18 → 45 RPS), coherente con un tiempo de espera de 0,5–1,5 s por usuario.
- En ambas corridas el perfil de 20 usuarios mostró picos aislados de 3–5 s que elevan el promedio pero no el p95, y la corrida 1 tuvo 7 fallos de conexión. **No se identificó la causa**: no se midieron CPU, memoria ni red, y servidor y generador comparten equipo. No se atribuye un cuello de botella sin esa evidencia.
- Sin un SLO acordado, estos datos caracterizan el comportamiento local observado; no acreditan un requisito de latencia.

## 7. Limitaciones

- Los resultados anteriores corresponden a la medición histórica en `stefven/calidad`. La configuración de CI está integrada en `main`.
- Mediciones en Windows con generador y servidor en el mismo equipo; no comparables con otro hardware.
- La interfaz se empaqueta junto a `sigen`. Consultar el [cierre de revisión](revision_despliegue.md).
- La medición de carga precede al empaquetado con Docker y al registro de tiempos. La tabla refleja el entorno indicado.
