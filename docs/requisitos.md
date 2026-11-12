# Requisitos del backend

Fuente normativa del proyecto: `SIGEN_Lite_Guia_Completa.md`, revisión del 10 de noviembre de 2026. La política de redondeo es una decisión asumida del simulador. Este documento registra únicamente el frente de Jose; no declara terminada la entrega completa.

| Requisito | Implementación / alcance | Verificación del frente |
|---|---|---|
| RF-01 | Formulario con tres nombres recortados de 1–80 caracteres. | tests/unit/test_calculator.py y tests/api/test_api.py: nombres, tamaño de arreglo, faltantes y extras. |
| RF-02 | Nota numérica finita de 0 a 5, múltiplo de 0.1, sin coerción. | Extremos, precisión, equivalencias numéricas y decodificación decimal. |
| RF-03 | Pesos enteros JSON de 0 a 100; suma 100. | 0/100, tipos, sumas 99/100/101 y precedencia de errores de campo. |
| RF-04 | Promedio puro con Decimal, sin redondeos intermedios. | Ejemplo 3.400 y promedios 2.949/2.950/2.951. |
| RF-05 | La interfaz muestra la definitiva HALF_UP y el estado según definitiva >=3.0. | Pruebas del motor, HTTP e interfaz. |
| RF-06 | Envoltorio de errores con código, mensaje y rutas presentados en la interfaz. | Errores HTTP 400/422/500 y regresión del foco. |
| RF-07 | Salud, cálculo y documentación OpenAPI. | Respuestas, cabeceras, esquemas y rutas de integración. |
| RF-08 | Formulario para recalcular con nuevas entradas y servidor sin persistencia. | Repetición de peticiones de cálculo en suite de API. |
| RF-09 | Fuera de la implementación inicial. | No implementado. |
| RNF-02 | Dominio y validación independientes de HTTP. | Pruebas unitarias sin FastAPI. |
| RNF-03 | Respuestas seguras y legibles. | Excepción sustituida en prueba: 500 genérico. |
| RNF-04 | Cobertura medida del backend y puerta de líneas ≥80 %. | `python scripts/verificar_calidad.py`. |
| RNF-05/06 | Carga, automatización y evidencia remota del proyecto. | Ver [reporte de calidad](reporte_calidad.md) y [GitHub Actions](https://github.com/Jacklb19/SIGEN/actions). |

La interfaz tiene una maqueta aprobada y comprobaciones manuales registradas en [pruebas de interfaz](pruebas_interfaz.md). La accesibilidad con lectores de pantalla queda pendiente de comprobación específica.

Toda modificación de reglas, códigos o tipos debe actualizar contrato, backend y pruebas, y coordinarse con los otros frentes. Las limitaciones académicas y los entregables finales siguen siendo los descritos en la guía.
