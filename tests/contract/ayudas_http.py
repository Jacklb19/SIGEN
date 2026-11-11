"""Comprobaciones HTTP reutilizables del contrato (sin fixtures)."""

import json
from decimal import Decimal

from contrato_esperado import TIPO_JSON, cargar_esquema
from jsonschema import Draft202012Validator

VALIDADORES = {
    nombre: Draft202012Validator(cargar_esquema(nombre))
    for nombre in ("salud", "entrada", "resultado", "error")
}


def cuerpo_decimal(respuesta):
    """Decodifica la respuesta conservando los decimales exactos emitidos."""
    return json.loads(respuesta.content, parse_float=Decimal)


def tipo_contenido(respuesta) -> str:
    return respuesta.headers.get("content-type", "").split(";")[0].strip()


def comprobar_json(respuesta, status: int, esquema: str):
    """Estado, Content-Type JSON y validez frente al esquema indicado."""
    assert respuesta.status_code == status, respuesta.text
    assert tipo_contenido(respuesta) == TIPO_JSON
    cuerpo = cuerpo_decimal(respuesta)
    errores = [e.message for e in VALIDADORES[esquema].iter_errors(cuerpo)]
    assert errores == [], errores
    return cuerpo


def comprobar_error(respuesta, status: int, codigo: str) -> set[tuple[str, str]]:
    """Valida el envoltorio y devuelve los pares (ruta, código) recibidos.

    Se comparan conjuntos: el contrato no garantiza el orden de los errores
    ni el texto literal de los mensajes.
    """
    cuerpo = comprobar_json(respuesta, status, "error")
    assert cuerpo["error"]["codigo"] == codigo
    return {(campo["ruta"], campo["codigo"]) for campo in cuerpo["error"]["campos"]}
