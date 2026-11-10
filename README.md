# SIGEN Lite

Sistema de Gestión y Evaluación de Notas Universitarias: prototipo académico para la asignatura **Pruebas y Mantenimiento de Software**.

Permitirá validar tres actividades evaluativas, calcular una definitiva ponderada y demostrar pruebas funcionales, de integración, contrato, cobertura, carga y mantenimiento.

## Estado actual

**Planificación y documentación inicial.** Todavía no hay aplicación, API, interfaz ni pruebas implementadas. No se han obtenido resultados de calidad o rendimiento. Los comandos de la guía describen la implementación prevista y aún no son ejecutables en este repositorio.

## Documentación

- [Guía completa: requisitos, contrato, arquitectura, pruebas y plan de trabajo](SIGEN_Lite_Guia_Completa.md).

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

Antes de desarrollar, revisar el contrato común de la guía. La interfaz requiere maqueta y plan aprobados antes de implementarse. Los comandos de instalación y ejecución se incorporarán y verificarán al desarrollar la aplicación.
