# SIGEN Lite

Sistema de Gestión y Evaluación de Notas Universitarias: prototipo académico para la asignatura **Pruebas y Mantenimiento de Software**.

Permitirá validar tres actividades evaluativas, calcular una definitiva ponderada y demostrar pruebas funcionales, de integración, contrato, cobertura, carga y mantenimiento.

## Estado actual

**Backend inicial implementado.** Ya existen motor Decimal, validaciones, API FastAPI, documentación OpenAPI y 119 pruebas del frente de Jose. La verificación local registró 100 % de líneas y ramas del backend, Ruff aprobado y Bandit sin hallazgos. Esto no acredita la entrega completa: interfaz, packaging, pruebas independientes, CI y carga siguen pendientes.

Las instrucciones temporales para ejecutar y probar la API están en [docs/backend.md](docs/backend.md). Los comandos de la guía que dependen de archivos todavía no implementados siguen siendo un plan, no resultados comprobados.

## Documentación

- [Guía completa: requisitos, contrato, arquitectura, pruebas y plan de trabajo](SIGEN_Lite_Guia_Completa.md).
- [Contrato de la API y acuerdos de integración](docs/contrato_api.md).
- [Requisitos y alcance del backend](docs/requisitos.md).
- [Ejecución, pruebas y pendientes del backend](docs/backend.md).

## Alcance inicial

- Tres actividades con nombre, nota entre 0 y 5 en incrementos de 0.1 y pesos enteros que suman 100.
- Cálculo interno con Decimal y redondeo HALF_UP a un decimal.
- Aprobación cuando la definitiva redondeada sea igual o superior a 3.0.
- API FastAPI e interfaz sencilla en HTML, CSS y JavaScript.
- Pruebas con Pytest, mínimo 80 % de líneas y reporte de ramas, Ruff, Bandit, Locust y CI.

Es un simulador con datos ficticios, sin cuentas, base de datos ni integración institucional. La política de redondeo es una decisión del prototipo, no una regla institucional certificada.

## Equipo

| Integrante | Frente |
|---|---|
| Jose | Motor, validaciones y API |
| Santiago | Interfaz y accesibilidad |
| Stefven | Pruebas independientes, configuración y evidencias |

Antes de desarrollar, revisar el contrato común de la guía y conservar la implementación existente. La interfaz requiere maqueta y plan aprobados antes de implementarse. Stefven preparará el paquete instalable, las dependencias fijadas y los comandos definitivos; mientras tanto, utilizar las instrucciones temporales del backend.
