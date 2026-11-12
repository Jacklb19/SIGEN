"""Esquemas públicos de OpenAPI 3.1 / JSON Schema 2020-12.

La validación operativa reside en validators. Un esquema no distingue el
token entero 30 del token decimal 30.0 ni comprueba la suma entre campos.
"""

from copy import deepcopy

from sigen.config import (
    ESCALAS_APROBACION,
    LONGITUD_NOMBRE_MAX,
    LONGITUD_NOMBRE_MIN,
    MAX_ACTIVIDADES,
    NOTA_MAX,
    NOTA_MIN,
    NUM_ACTIVIDADES,
    PASO_NOTA,
    PESO_MAX,
    PESO_MIN,
    TOTAL_PESOS,
)

ENTRADA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["actividades"],
    "properties": {
        "actividades": {
            "type": "array",
            "minItems": NUM_ACTIVIDADES,
            "maxItems": NUM_ACTIVIDADES,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["nombre", "nota", "peso"],
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Se recorta antes de validar su longitud.",
                    },
                    "nota": {
                        "type": "number",
                        "minimum": float(NOTA_MIN),
                        "maximum": float(NOTA_MAX),
                        "multipleOf": float(PASO_NOTA),
                    },
                    "peso": {
                        "type": "integer",
                        "minimum": PESO_MIN,
                        "maximum": PESO_MAX,
                        "description": "Entero JSON sin coerción; 30.0 no se admite.",
                    },
                },
            },
        }
    },
}
ENTRADA_SCHEMA["properties"]["actividades"]["items"]["properties"]["nombre"][
    "description"
] += f" Debe quedar entre {LONGITUD_NOMBRE_MIN} y {LONGITUD_NOMBRE_MAX} caracteres."

RESULTADO_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "promedio_ponderado",
        "nota_definitiva",
        "estado",
        "ponderacion_total",
    ],
    "properties": {
        "promedio_ponderado": {
            "type": "number",
            "minimum": float(NOTA_MIN),
            "maximum": float(NOTA_MAX),
        },
        "nota_definitiva": {
            "type": "number",
            "minimum": float(NOTA_MIN),
            "maximum": float(NOTA_MAX),
            "multipleOf": float(PASO_NOTA),
        },
        "estado": {"type": "string", "enum": ["APROBADO", "REPROBADO"]},
        "ponderacion_total": {"type": "integer", "const": TOTAL_PESOS},
    },
}

ERROR_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "additionalProperties": False,
            "required": ["codigo", "mensaje", "campos"],
            "properties": {
                "codigo": {
                    "type": "string",
                    "enum": ["VALIDACION", "PONDERACION_INVALIDA", "ERROR_INTERNO"],
                },
                "mensaje": {"type": "string"},
                "campos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["ruta", "codigo", "mensaje"],
                        "properties": {
                            "ruta": {"type": "string"},
                            "codigo": {"type": "string"},
                            "mensaje": {"type": "string"},
                        },
                    },
                },
            },
        }
    },
}


def _entrada_en_escala(escala: int) -> dict:
    esquema = deepcopy(ENTRADA_SCHEMA)
    esquema["required"].append("escala")
    propiedades = esquema["properties"]
    propiedades["escala"] = {"type": "integer", "const": escala}
    actividades = propiedades["actividades"]
    actividades["maxItems"] = MAX_ACTIVIDADES
    actividades["items"]["properties"]["nota"]["maximum"] = escala
    return esquema


ENTRADA_FLEXIBLE_SCHEMA = {
    "oneOf": [_entrada_en_escala(escala) for escala in ESCALAS_APROBACION]
}
RESULTADO_FLEXIBLE_SCHEMA = deepcopy(RESULTADO_SCHEMA)
for campo in ("promedio_ponderado", "nota_definitiva"):
    RESULTADO_FLEXIBLE_SCHEMA["properties"][campo]["maximum"] = max(ESCALAS_APROBACION)
