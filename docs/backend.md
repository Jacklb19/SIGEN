# Backend de Jose

## Estado

El backend sirve la interfaz integrada, los endpoints de salud y cálculo y la documentación OpenAPI. El proyecto dispone de dependencias fijadas, pruebas independientes, CI, Docker y evidencias de Locust. El paquete incluye los archivos HTML, CSS y JavaScript.

El [README](../README.md) contiene los comandos vigentes. Los resultados anteriores a la integración se conservan en el [reporte de calidad](reporte_calidad.md).

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

## Ejecución

Después de instalar las dependencias y el paquete con los pasos del README, arrancar el servidor:

```powershell
python -m uvicorn sigen.api:app
```

Abrir `/` para la interfaz y `/docs` para probar salud y cálculo. La entrada para Vercel está en `src/app.py`. Las rutas HTTP mantienen el contrato documentado.

## Comprobaciones

Desde la raíz en PowerShell:

```powershell
python scripts/verificar_calidad.py
python -m ruff check .
python -m ruff format --check .
python -m bandit -c pyproject.toml -r src -q
```

El cliente ASGI de Starlette usa httpx2. El contrato contra el servidor HTTP usa Requests. El registro de Uvicorn incluye método, ruta, estado y duración. El encabezado `Server-Timing` permite consultar el tiempo en las herramientas del navegador. Consultar las verificaciones de integración en el [cierre de revisión](revision_despliegue.md).
