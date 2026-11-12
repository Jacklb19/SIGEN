# Sustentación y entrega de SIGEN Lite

| Tiempo | Demostración | Evidencia |
|---|---|---|
| 0:00–0:45 | Presentar el problema y las tres actividades ponderadas. | README y requisitos. |
| 0:45–2:00 | Calcular 3.4, rechazar una nota de 5.1, probar suma 110 y mostrar el redondeo 2.95 → 3.0. | Interfaz y contrato. |
| 2:00–3:30 | Mostrar una prueba con AAA, los valores límite y la puerta de cobertura. | Pytest, matriz y artefacto de CI. |
| 3:30–4:30 | Abrir OpenAPI y explicar cómo Requests y JSON Schema verifican el contrato. | `/docs` y suite `tests/contract`. |
| 4:30–5:30 | Mostrar CI, Docker y el reporte Locust. Explicar p95, solicitudes por segundo y fallos observados. | GitHub Actions y reporte de calidad. |
| 5:30–6:30 | Mostrar los commits que reproducen y corrigen precisión y foco. | Historial y regresiones de interfaz. |
| 6:30–7:00 | Cerrar con resultados, límites y alcance del despliegue. | Informe de revisión y evidencia disponible. |

Entregar el enlace al repositorio, el enlace a la ejecución verde de GitHub Actions, la matriz de pruebas, la evidencia de Locust y el historial de mantenimiento. Descargar el artefacto de cobertura de la ejecución que se vaya a presentar. Adjuntar capturas de la demo y del reporte si las pide el profesor. Si se activa SonarQube Cloud, añadir el enlace y el resultado real del análisis. Si se publica en Vercel, añadir la URL comprobada.

El sistema reduce errores de rango, ponderación y redondeo mediante validaciones y pruebas de frontera. Las regresiones de interfaz cubren dos defectos que escapaban a las pruebas Python. La medición de carga describe el entorno local documentado. La política de redondeo corresponde al prototipo académico.
