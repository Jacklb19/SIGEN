"""Motor puro: Decimal y política asumida de redondeo del prototipo."""

from decimal import Decimal, localcontext

from sigen.config import (
    ESCALAS_APROBACION,
    NOTA_APROBACION,
    PASO_NOTA,
    PRECISION_CALCULO,
    REDONDEO,
    TOTAL_PESOS,
)
from sigen.domain import Actividad, DatosInvalidos, ErrorCampo, Estado, Resultado
from sigen.validators import validar_entrada


def calcular_promedio(actividades: tuple[Actividad, ...]) -> Decimal:
    """Recibe actividades ya normalizadas por validar_entrada."""
    with localcontext() as contexto:
        contexto.prec = PRECISION_CALCULO
        return sum(
            (
                actividad.nota * actividad.peso / TOTAL_PESOS
                for actividad in actividades
            ),
            start=Decimal(0),
        )


def obtener_estado(definitiva: Decimal, *, umbral: Decimal = NOTA_APROBACION) -> Estado:
    """Compara la definitiva, nunca el promedio bruto."""
    return Estado.APROBADO if definitiva >= umbral else Estado.REPROBADO


def calcular_resultado(datos: object) -> Resultado:
    return _calcular(validar_entrada(datos), NOTA_APROBACION)


def calcular_resultado_flexible(datos: object) -> Resultado:
    escala = datos.get("escala") if isinstance(datos, dict) else None
    if type(escala) is not int or escala not in ESCALAS_APROBACION:
        raise DatosInvalidos(
            [
                ErrorCampo(
                    "escala", "ESCALA_INVALIDA", "Selecciona una escala de 5 o 10."
                )
            ]
        )
    return _calcular(validar_entrada(datos, escala=escala), ESCALAS_APROBACION[escala])


def _calcular(actividades: tuple[Actividad, ...], umbral: Decimal) -> Resultado:
    promedio = calcular_promedio(actividades)
    with localcontext() as contexto:
        contexto.prec = PRECISION_CALCULO
        definitiva = promedio.quantize(PASO_NOTA, rounding=REDONDEO)
    estado = obtener_estado(definitiva, umbral=umbral)
    return Resultado(promedio, definitiva, estado, TOTAL_PESOS)
