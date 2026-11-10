"""Motor puro: Decimal y política asumida de redondeo del prototipo."""

from decimal import Decimal, localcontext

from sigen.config import (
    NOTA_APROBACION,
    PASO_NOTA,
    PRECISION_CALCULO,
    REDONDEO,
    TOTAL_PESOS,
)
from sigen.domain import Actividad, Estado, Resultado
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


def obtener_estado(definitiva: Decimal) -> Estado:
    """Compara la definitiva, nunca el promedio bruto."""
    return Estado.APROBADO if definitiva >= NOTA_APROBACION else Estado.REPROBADO


def calcular_resultado(datos: object) -> Resultado:
    actividades = validar_entrada(datos)
    promedio = calcular_promedio(actividades)
    with localcontext() as contexto:
        contexto.prec = PRECISION_CALCULO
        definitiva = promedio.quantize(PASO_NOTA, rounding=REDONDEO)
    return Resultado(promedio, definitiva, obtener_estado(definitiva), TOTAL_PESOS)
