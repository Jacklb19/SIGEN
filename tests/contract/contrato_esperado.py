"""Contrato esperado, transcrito de la guía §5 y de docs/contrato_api.md.

Es deliberadamente independiente de ``sigen.config`` y ``sigen.schemas``: si el
backend cambia un límite, una ruta o un código sin coordinarlo, estas pruebas
deben detectarlo en lugar de adaptarse en silencio.
"""

import copy
import json
from decimal import Decimal
from pathlib import Path

RUTA_SALUD = "/health"
RUTA_CALCULO = "/api/v1/calcular"
TIPO_JSON = "application/json"

CUERPO_SALUD = {"status": "ok", "service": "sigen-lite"}

NOMBRE_MAX = 80
TOTAL_PESOS = 100

# Códigos generales y por campo (guía §5.2).
VALIDACION = "VALIDACION"
PONDERACION_INVALIDA = "PONDERACION_INVALIDA"
ERROR_INTERNO = "ERROR_INTERNO"
JSON_INVALIDO = "JSON_INVALIDO"
REQUERIDO = "REQUERIDO"
TIPO = "TIPO"
RANGO = "RANGO"
PRECISION = "PRECISION"
LONGITUD = "LONGITUD"
CAMPO_DESCONOCIDO = "CAMPO_DESCONOCIDO"
CANTIDAD = "CANTIDAD"
SUMA_PESOS = "SUMA_PESOS"
RUTA_BODY = "body"
RUTA_ACTIVIDADES = "actividades"
RUTA_PESOS = "actividades.pesos"

CLAVES_RESULTADO = {
    "promedio_ponderado",
    "nota_definitiva",
    "estado",
    "ponderacion_total",
}

EJEMPLO_GUIA = {
    "actividades": [
        {"nombre": "Parcial 1", "nota": 3.5, "peso": 30},
        {"nombre": "Parcial 2", "nota": 2.5, "peso": 30},
        {"nombre": "Proyecto", "nota": 4.0, "peso": 40},
    ]
}

DIRECTORIO_ESQUEMAS = Path(__file__).resolve().parent / "esquemas"


def peticion(notas=(3.5, 2.5, 4.0), pesos=(30, 30, 40), nombres=None):
    """Construye una petición de tres actividades a partir del ejemplo."""
    datos = copy.deepcopy(EJEMPLO_GUIA)
    nombres = nombres or [a["nombre"] for a in datos["actividades"]]
    for actividad, nombre, nota, peso in zip(
        datos["actividades"], nombres, notas, pesos, strict=True
    ):
        actividad.update(nombre=nombre, nota=nota, peso=peso)
    return datos


def cuerpo_bruto(nota: str = "3.5", peso: str = "30") -> str:
    """Texto JSON del ejemplo con tokens literales en la primera actividad.

    Permite enviar escrituras que json.dumps no produce (3.50, 35e-1, 30.0)
    y cuerpos que no son JSON estándar (NaN, Infinity) como bytes brutos.
    """
    return (
        '{"actividades": ['
        f'{{"nombre": "Parcial 1", "nota": {nota}, "peso": {peso}}}, '
        '{"nombre": "Parcial 2", "nota": 2.5, "peso": 30}, '
        '{"nombre": "Proyecto", "nota": 4.0, "peso": 40}]}'
    )


def ruta_actividad(indice: int, campo: str | None = None) -> str:
    ruta = f"{RUTA_ACTIVIDADES}.{indice}"
    return f"{ruta}.{campo}" if campo else ruta


def cargar_esquema(nombre: str) -> dict:
    """Carga el esquema con Decimal para que multipleOf 0.1 sea exacto."""
    texto = (DIRECTORIO_ESQUEMAS / f"{nombre}.schema.json").read_text(encoding="utf-8")
    return json.loads(texto, parse_float=Decimal)


def como_json_decimal(objeto):
    """Serializa y decodifica como lo haría HTTP, con decimales exactos."""
    return json.loads(json.dumps(objeto), parse_float=Decimal)
