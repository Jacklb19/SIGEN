# Backend de Jose

## Estado

Implementados el dominio, la validación, el cálculo, los endpoints de salud y cálculo, el esquema OpenAPI y el montaje previsto de la interfaz. La interfaz de Santiago aún no existe. El entorno reproducible del proyecto, dependencias fijadas, pruebas independientes, CI y Locust corresponden a Stefven.

El README registra este avance inicial. Stefven completará sus instrucciones definitivas al integrar packaging, dependencias y calidad transversal; este archivo conserva el detalle comprobado del frente de Jose.

## Organización

- `src/sigen/config.py`: reglas y rutas compartidas.
- `src/sigen/domain.py`: objetos inmutables y errores sin HTTP.
- `src/sigen/validators.py`: validación única y normalización.
- `src/sigen/calculator.py`: promedio, definitiva y estado con Decimal.
- `src/sigen/schemas.py`: contrato de entrada, salida y errores para OpenAPI.
- `src/sigen/api.py`: decodificación decimal, adaptador HTTP y archivos estáticos.
- `tests/unit/`: reglas y motor.
- `tests/api/`: integración HTTP del frente, documentación y montaje estático.

`calcular_resultado` recibe el objeto ya decodificado, valida y calcula. Los decimales internos se pasan como Decimal; los enteros como int. Rechaza floats internos para evitar introducir representaciones binarias accidentales. `calcular_promedio` recibe actividades ya validadas; `obtener_estado` recibe la definitiva ya redondeada. La ruta HTTP conserva números decimales mediante parse_float=Decimal.

## Ejecución temporal mientras se prepara el packaging

El proyecto aún no tiene pyproject ni requirements: no declarar instalado el paquete. El entorno `.venv` de esta sesión es local y está ignorado en Git. Para reproducir las dependencias directas verificadas con Python 3.11:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi==0.162.4 uvicorn==0.54.0 httpx==0.28.1 pytest==9.2.0 pytest-cov==7.1.0 ruff==0.17.4 bandit==1.9.4 jsonschema==4.26.0
.\.venv\Scripts\python.exe -m uvicorn sigen.api:app --app-dir src --reload
```

Esos pins de dependencias directas documentan la comprobación actual; no equivalen a un lock completo ni sustituyen el trabajo de fijar dependencias transitivas y packaging de Stefven. Python en el entorno comprobado: 3.11.16. Pydantic: 2.14.3; Starlette: 1.10.0.

Tras configurar el paquete instalable, ejecutar el servidor como indica la guía, sin necesitar `--app-dir src`. No usar reload para medir carga. Abrir `/docs` para probar salud y cálculo; `/` devuelve 404 hasta que exista `web/index.html`. Reiniciar al agregar `web/` para registrar `/static`.

## Comprobaciones

Desde la raíz en PowerShell:

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m pytest tests/unit tests/api -q --cov=sigen --cov-branch --cov-report=term-missing --cov-report=json:coverage.json
.\.venv\Scripts\python.exe -m ruff check src/sigen tests/unit tests/api
.\.venv\Scripts\python.exe -m ruff format --check src/sigen tests/unit tests/api
.\.venv\Scripts\python.exe -m bandit -r src/sigen -q
```

Comprobación del 10 de noviembre de 2026: **119 pruebas aprobadas**, 203 sentencias productivas cubiertas de 203 y 50 ramas cubiertas de 50. El JSON de cobertura es un reporte generado e ignorado en Git. Esta medición corresponde al backend actual, no acredita componentes pendientes ni ausencia de defectos. El comando único y la puerta global se implementarán por Stefven.

Ruff check aprobado, nueve archivos Python con formato verificado y Bandit sin hallazgos en `src/sigen`. También se comprobó explícitamente la proporción de líneas a partir de `coverage.json`, sin usar el porcentaje combinado de líneas y ramas como sustituto.

La primera ejecución de integración dentro del sandbox falló al crear las carpetas temporales de Pytest. Se repitió con los permisos necesarios y pasó. No se modificaron las aserciones para sortear el problema de entorno.

La combinación instalada emite una advertencia de Starlette: el uso de httpx con TestClient está deprecado y recomienda httpx2. Las pruebas pasan, pero Stefven debe resolver y fijar una combinación compatible o evaluar esa migración al preparar las dependencias. No se ocultó la advertencia ni se incorporó otra dependencia sin esa evaluación.

## Integración pendiente

1. Santiago: revisar `docs/contrato_api.md`, presentar y obtener aprobación de la maqueta, implementar `web/` y conectar la API real. El backend ya contempla el montaje.
2. Stefven: preparar packaging/dependencias y comando único de calidad; añadir pruebas independientes, CI, carga y evidencia; actualizar el README con el estado integrado.
3. Equipo: confirmar con la rúbrica los complementos académicos y coordinar cualquier cambio de contrato.

No se ejecutaron Locust, CI remota ni pruebas de una interfaz real. La publicación del backend en Git se realiza con autorización expresa de Jose, con su autoría exclusiva y sin coautorías. No incluye merges ni despliegues de la aplicación.
