"""Objetos inmutables y errores del dominio, sin dependencias HTTP."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Estado(str, Enum):
    APROBADO = "APROBADO"
    REPROBADO = "REPROBADO"


@dataclass(frozen=True)
class Actividad:
    nombre: str
    nota: Decimal
    peso: int


@dataclass(frozen=True)
class Resultado:
    promedio_ponderado: Decimal
    nota_definitiva: Decimal
    estado: Estado
    ponderacion_total: int


@dataclass(frozen=True)
class ErrorCampo:
    ruta: str
    codigo: str
    mensaje: str


class DatosInvalidos(ValueError):
    """Errores de campos; no incluye valores sensibles de la entrada."""

    codigo = "VALIDACION"
    mensaje = "Revisa los datos."

    def __init__(self, campos: list[ErrorCampo]):
        self.campos = tuple(campos)
        super().__init__(self.mensaje)


class PonderacionInvalida(DatosInvalidos):
    codigo = "PONDERACION_INVALIDA"
    mensaje = "Los porcentajes deben sumar 100."
