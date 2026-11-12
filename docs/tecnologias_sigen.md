# Tecnologías de SIGEN Lite

Guía para la sustentación de Pruebas y Mantenimiento de Software. Empieza con el recorrido de una solicitud y abre los archivos según lo que te pregunte el profesor.

> El navegador recoge tres actividades y envía sus datos por HTTP. FastAPI recibe el JSON, Python comprueba las reglas y calcula la definitiva. GitHub Actions ejecuta las verificaciones de cada cambio. Docker permite repetir las pruebas en un entorno reproducible y Vercel aloja la aplicación.

## Aplicación y contrato

| Tecnología | Qué es | Para qué se usó en SIGEN | Dónde mostrarla |
|---|---|---|---|
| HTML | Lenguaje que define la estructura de una página. | Formulario con tres actividades, campos etiquetados y sección de resultado. En esta rama también contiene el campo opcional de materia y el indicador de pesos. | [index.html](../src/sigen/web/index.html) |
| CSS | Lenguaje para la presentación de una página. | Diseño adaptable, barra de pesos, estados y énfasis en la definitiva. | [styles.css](../src/sigen/web/styles.css) |
| JavaScript | Lenguaje que ejecuta el navegador. | Valida lo escrito, actualiza el total de pesos, envía el JSON con `fetch` y presenta el resultado. La materia se utiliza como etiqueta en pantalla. | [app.js](../src/sigen/web/app.js), funciones `actualizarTotalPesos`, `construirCarga` y `calcular` |
| Python y Decimal | Lenguaje del servidor y tipo de aritmética decimal de su biblioteca estándar. | Aplica los límites y calcula `suma(nota × peso / 100)`. Redondea a un decimal con `ROUND_HALF_UP` y compara la definitiva con 3.0. | [config.py](../src/sigen/config.py), [validators.py](../src/sigen/validators.py), [calculator.py](../src/sigen/calculator.py) |
| FastAPI y Uvicorn | FastAPI define la aplicación HTTP. Uvicorn es el servidor ASGI que la ejecuta localmente y en Docker. | Exponen `/health`, `/docs`, la interfaz y `POST /api/v1/calcular`. La API decodifica los números con Decimal y convierte los errores a respuestas HTTP. | [api.py](../src/sigen/api.py), [Dockerfile](../Dockerfile) y [README](../README.md) |
| OpenAPI y JSON Schema | OpenAPI documenta rutas y operaciones. JSON Schema describe la estructura y los tipos de los documentos JSON. | Documentan entrada, resultado y errores. Las pruebas usan esquemas independientes para detectar cambios que rompan el contrato. | [schemas.py](../src/sigen/schemas.py), [contrato](contrato_api.md), [esquemas de prueba](../tests/contract/esquemas/) |

## Pruebas y análisis

| Tecnología o técnica | Qué es | Para qué se usó en SIGEN | Dónde mostrarla |
|---|---|---|---|
| Pytest | Ejecutor de pruebas de Python. | Comprueba el cálculo aislado, los endpoints, el contrato y la puerta de cobertura. | [tests/unit](../tests/unit/), [tests/api](../tests/api/), [tests/contract](../tests/contract/) y [tests/calidad](../tests/calidad/) |
| AAA, valores límite y parametrización | AAA significa preparar, ejecutar y comprobar. Parametrizar permite reutilizar un caso con distintos datos. | Prueba notas como 0, 5, −0.1 y 5.1 y los promedios 2.949, 2.950 y 2.951 alrededor del punto de redondeo. | [test_calculator.py](../tests/unit/test_calculator.py) |
| Requests, TestClient y httpx2 | Requests es un cliente HTTP. TestClient permite probar la app ASGI en el mismo proceso y usa httpx2 en este proyecto. | Con `SIGEN_URL_BASE` se usa Requests contra Uvicorn. La misma suite puede ejecutarse en proceso con TestClient. | [conftest.py](../tests/contract/conftest.py) y [ayudas_http.py](../tests/contract/ayudas_http.py) |
| Node.js y node:test | Entorno para ejecutar JavaScript y su ejecutor de pruebas incorporado. | Comprueban las regresiones de precisión y foco. En esta rama también verifican el indicador de pesos y que la materia permanezca fuera de la petición HTTP. | [test_interfaz.cjs](../tests/ui/test_interfaz.cjs) |
| pytest-cov | Complemento de Pytest para medir cobertura. | Genera reportes de líneas y ramas. El script aplica un mínimo del 80 % de líneas y reporta las ramas por separado. | [verificar_calidad.py](../scripts/verificar_calidad.py) y [pyproject.toml](../pyproject.toml) |
| Ruff y Bandit | Ruff comprueba reglas de estilo y calidad de Python. Bandit busca patrones asociados con riesgos de seguridad. | Ejecutan análisis estático del código como parte de CI. | [pyproject.toml](../pyproject.toml), [ci.yml](../.github/workflows/ci.yml) y [reporte de calidad](reporte_calidad.md) |
| SonarQube Cloud | Servicio de análisis estático con métricas y un Quality Gate. | Recibe el análisis de GitHub Actions e importa `coverage.xml`. El resultado del Quality Gate se consulta en el panel de Sonar. | [sonar-project.properties](../sonar-project.properties), [ci.yml](../.github/workflows/ci.yml) y [panel de SIGEN](https://sonarcloud.io/dashboard?id=Jacklb19_SIGEN&branch=main) |
| Locust | Herramienta para simular usuarios concurrentes. | Ejecutó perfiles de 10, 20 y 50 usuarios. El reporte presenta latencia, solicitudes por segundo y fallos. Los errores HTTP esperados forman parte de la verificación. | [locustfile.py](../locustfile.py), [reporte de calidad](reporte_calidad.md) y [CSV de carga](evidencias/carga/) |

## DevOps, mantenimiento y despliegue

| Tecnología o práctica | Qué es y para qué se usó | Evidencia |
|---|---|---|
| Git | Control de versiones. El historial conserva los cambios y permite mostrar cuándo una prueba reprodujo un fallo y cuándo se corrigió. | [mantenimiento.md](mantenimiento.md) |
| GitHub Actions | Integración continua. Ejecuta la suite, la cobertura, Ruff, Bandit, las pruebas de interfaz y la verificación de Docker. El análisis Sonar se ejecuta en pushes a `main` con sus claves configuradas. | [ci.yml](../.github/workflows/ci.yml) y [ejecución con Sonar](https://github.com/Jacklb19/SIGEN/actions/runs/43161634089) |
| Docker | Empaqueta la aplicación y sus dependencias. El Dockerfile tiene una etapa de pruebas y una imagen de ejecución. CI comprueba ambas. | [Dockerfile](../Dockerfile) y [.dockerignore](../.dockerignore) |
| Vercel | Plataforma que aloja la app. `src/app.py` exporta FastAPI, se fija Python 3.12 y los archivos web van dentro del paquete. Si la integración Git publica automáticamente un push a `main`, su historial sirve para demostrar CD. | [src/app.py](../src/app.py), [.python-version](../.python-version) y [guía de despliegue](despliegue_vercel.md) |
| Observabilidad básica | El middleware registra método, ruta, estado y duración. El encabezado `Server-Timing` permite consultar el tiempo de respuesta en el navegador. | [api.py](../src/sigen/api.py), función `medir_solicitud` |
| Variables y secretos | Las claves del proyecto identifican la organización y el proyecto en Sonar. El token se almacena como secreto de GitHub Actions. | Paso SonarQube Cloud en [ci.yml](../.github/workflows/ci.yml) |

## Tres preguntas para ensayar

1. **¿Dónde se decide si aprueba?** En `obtener_estado`, dentro de `calculator.py`. Compara la definitiva redondeada con 3.0. Para demostrarlo, usa notas 2.9, 3.0 y 0 con pesos 50, 50 y 0. El promedio es 2.950 y la definitiva es 3.0.
2. **¿Qué demuestra el 100 % de cobertura?** Que la suite ejecutó las líneas y ramas medidas del backend en esa corrida. Para demostrar que una prueba detecta un defecto, muestra el caso que falla antes de corregirlo y pasa después.
3. **¿Cuál es la diferencia entre CI y CD en SIGEN?** CI verifica cambios en GitHub Actions. CD publica una versión mediante la integración de Vercel, cuando está configurada. Enseña el historial de cada servicio como evidencia.

Para ordenar la demostración, consulta el [guion de sustentación](sustentacion.md).

## Cómo explicar la ampliación

La interfaz guarda un borrador en memoria por semestre en [app.js](../src/sigen/web/app.js). En [index.html](../src/sigen/web/index.html) se eligen semestre, escala y actividades. La API añade `POST /api/v2/calcular` en [api.py](../src/sigen/api.py), con los límites en [validators.py](../src/sigen/validators.py) y el umbral por escala en [calculator.py](../src/sigen/calculator.py).

Para mostrar el cambio, selecciona la escala de 0 a 10 y agrega una cuarta actividad. Usa notas 7, 8, 7 y 8 con peso 25 para cada una. Debe dar 7.5 y APROBADO. Cambia de semestre y vuelve para mostrar que cada formulario se conserva durante la sesión. La suite prueba v1 y v2, incluidos el límite de actividades y el caso 5.95 → 6.0 sobre 10. [Pruebas de v2](../tests/api/test_calculo_flexible.py) · [Pruebas de interfaz](../tests/ui/test_interfaz.cjs)
