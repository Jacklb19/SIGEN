"""Validación única para entradas decodificadas y objetos del dominio."""

from decimal import Decimal, localcontext

from sigen.config import (
    LONGITUD_NOMBRE_MAX,
    LONGITUD_NOMBRE_MIN,
    NOTA_MAX,
    NOTA_MIN,
    NUM_ACTIVIDADES,
    PASO_NOTA,
    PESO_MAX,
    PESO_MIN,
    PRECISION_CALCULO,
    TOTAL_PESOS,
)
from sigen.domain import (
    Actividad,
    DatosInvalidos,
    ErrorCampo,
    PonderacionInvalida,
)


def _fallar(ruta: str, codigo: str, mensaje: str) -> None:
    raise DatosInvalidos([ErrorCampo(ruta, codigo, mensaje)])


def validar_nombre(valor: object, ruta: str = "nombre") -> str:
    if not isinstance(valor, str):
        _fallar(ruta, "TIPO", "El nombre debe ser texto.")
    nombre = valor.strip()
    if not LONGITUD_NOMBRE_MIN <= len(nombre) <= LONGITUD_NOMBRE_MAX:
        _fallar(
            ruta,
            "LONGITUD",
            f"El nombre debe tener entre {LONGITUD_NOMBRE_MIN} "
            f"y {LONGITUD_NOMBRE_MAX} caracteres.",
        )
    return nombre


def validar_nota(valor: object, ruta: str = "nota") -> Decimal:
    # bool hereda de int: la comprobación debe ser exacta.
    # Los floats del JSON ya deben haberse decodificado como Decimal.
    if type(valor) not in (int, Decimal):
        _fallar(ruta, "TIPO", "La nota debe ser un número.")
    nota = Decimal(valor)
    if not nota.is_finite() or not NOTA_MIN <= nota <= NOTA_MAX:
        _fallar(ruta, "RANGO", "La nota debe estar entre 0 y 5 y ser finita.")
    with localcontext() as contexto:
        contexto.prec = PRECISION_CALCULO
        normalizada = nota.quantize(PASO_NOTA)
    if nota != normalizada:
        _fallar(ruta, "PRECISION", "La nota debe ser múltiplo de 0.1.")
    return normalizada


def validar_peso(valor: object, ruta: str = "peso") -> int:
    if type(valor) is not int:
        _fallar(ruta, "TIPO", "El porcentaje debe ser un entero JSON.")
    if not PESO_MIN <= valor <= PESO_MAX:
        _fallar(ruta, "RANGO", "El porcentaje debe estar entre 0 y 100.")
    return valor


def validar_pesos(pesos: list[object]) -> tuple[int, ...]:
    if len(pesos) != NUM_ACTIVIDADES:
        _fallar("actividades", "CANTIDAD", "Se requieren tres actividades.")
    errores: list[ErrorCampo] = []
    validos = []
    for indice, peso in enumerate(pesos):
        try:
            validos.append(validar_peso(peso, f"actividades.{indice}.peso"))
        except DatosInvalidos as error:
            errores.extend(error.campos)
    if errores:
        raise DatosInvalidos(errores)
    if sum(validos) != TOTAL_PESOS:
        raise PonderacionInvalida(
            [
                ErrorCampo(
                    "actividades.pesos", "SUMA_PESOS", "Los pesos deben sumar 100."
                )
            ]
        )
    return tuple(validos)


def _validar_claves(datos: dict, requeridas: set[str], ruta: str) -> list[ErrorCampo]:
    errores = []
    for clave in sorted(requeridas - datos.keys()):
        campo = f"{ruta}.{clave}" if ruta else clave
        errores.append(ErrorCampo(campo, "REQUERIDO", "El campo es requerido."))
    for clave in datos.keys() - requeridas:
        campo = f"{ruta}.{clave}" if ruta else str(clave)
        errores.append(ErrorCampo(campo, "CAMPO_DESCONOCIDO", "Campo no permitido."))
    return errores


def validar_entrada(datos: object) -> tuple[Actividad, ...]:
    if not isinstance(datos, dict):
        _fallar("body", "TIPO", "La petición debe ser un objeto JSON.")
    errores = _validar_claves(datos, {"actividades"}, "")
    actividades = datos.get("actividades")
    if "actividades" not in datos:
        raise DatosInvalidos(errores)
    if not isinstance(actividades, list):
        errores.append(ErrorCampo("actividades", "TIPO", "Se requiere una lista."))
        raise DatosInvalidos(errores)
    if len(actividades) != NUM_ACTIVIDADES:
        errores.append(
            ErrorCampo("actividades", "CANTIDAD", "Se requieren tres actividades.")
        )
        raise DatosInvalidos(errores)

    validadas = []
    validadores = {"nombre": validar_nombre, "nota": validar_nota, "peso": validar_peso}
    for indice, actividad in enumerate(actividades):
        ruta = f"actividades.{indice}"
        if not isinstance(actividad, dict):
            errores.append(ErrorCampo(ruta, "TIPO", "La actividad debe ser un objeto."))
            continue
        errores.extend(_validar_claves(actividad, set(validadores), ruta))
        valores = {}
        for clave, validar in validadores.items():
            if clave in actividad:
                try:
                    valores[clave] = validar(actividad[clave], f"{ruta}.{clave}")
                except DatosInvalidos as error:
                    errores.extend(error.campos)
        if len(valores) == len(validadores):
            validadas.append(Actividad(**valores))
    if errores:
        raise DatosInvalidos(errores)
    validar_pesos([actividad.peso for actividad in validadas])
    return tuple(validadas)
