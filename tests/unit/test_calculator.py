"""Pruebas del dominio y del cálculo, sin HTTP."""

from decimal import Decimal, localcontext

import pytest

from sigen.calculator import calcular_resultado, obtener_estado
from sigen.domain import DatosInvalidos, Estado, PonderacionInvalida
from sigen.validators import (
    validar_entrada,
    validar_nombre,
    validar_nota,
    validar_pesos,
)


def entrada(notas=("3.5", "2.5", "4.0"), pesos=(30, 30, 40)):
    return {
        "actividades": [
            {"nombre": f"Actividad {i + 1}", "nota": Decimal(nota), "peso": peso}
            for i, (nota, peso) in enumerate(zip(notas, pesos, strict=True))
        ]
    }


@pytest.mark.parametrize("nota", ["0", "0.1", "4.9", "5", "3.50", "35e-1"])
def test_notas_validas(nota):
    assert validar_nota(Decimal(nota)) == Decimal(nota)


@pytest.mark.parametrize(
    "nota,codigo",
    [
        (Decimal("-0.1"), "RANGO"),
        (Decimal("5.1"), "RANGO"),
        (Decimal("3.55"), "PRECISION"),
        (Decimal("1e-1000"), "PRECISION"),
        (Decimal("NaN"), "RANGO"),
        (Decimal("sNaN"), "RANGO"),
        (Decimal("Infinity"), "RANGO"),
        (Decimal("1e1000"), "RANGO"),
        ("4.5", "TIPO"),
        (True, "TIPO"),
        (None, "TIPO"),
        (3.5, "TIPO"),
    ],
)
def test_notas_invalidas(nota, codigo):
    with pytest.raises(DatosInvalidos) as error:
        validar_nota(nota)
    assert error.value.campos[0].codigo == codigo


@pytest.mark.parametrize("nota", [0, 3, 5])
def test_notas_enteras(nota):
    assert validar_nota(nota) == Decimal(nota)


@pytest.mark.parametrize("nombre", ["A", "A" * 80, "  Proyecto  "])
def test_nombre_recortado(nombre):
    assert validar_nombre(nombre) == nombre.strip()


@pytest.mark.parametrize("nombre", ["", " \t\n ", "A" * 81, None, 3, True])
def test_nombre_invalido(nombre):
    with pytest.raises(DatosInvalidos):
        validar_nombre(nombre)


@pytest.mark.parametrize("pesos", [[30, 30, 40], [100, 0, 0], [0, 50, 50]])
def test_pesos_validos(pesos):
    assert validar_pesos(pesos) == tuple(pesos)


@pytest.mark.parametrize("pesos", [[30, 30, 39], [30, 30, 41]])
def test_pesos_suma_invalida(pesos):
    with pytest.raises(PonderacionInvalida) as error:
        validar_pesos(pesos)
    assert error.value.campos[0].ruta == "actividades.pesos"


@pytest.mark.parametrize(
    "pesos", [[-1, 1, 100], [101, 0, 0], [30, 30.0, 40], [True, 49, 50], [50, 50]]
)
def test_pesos_tipo_rango_o_cantidad(pesos):
    with pytest.raises(DatosInvalidos) as error:
        validar_pesos(pesos)
    assert not isinstance(error.value, PonderacionInvalida)


def test_ejemplo_aritmetico():
    resultado = calcular_resultado(entrada())
    assert resultado.promedio_ponderado == Decimal("3.400")
    assert resultado.nota_definitiva == Decimal("3.4")
    assert resultado.estado == Estado.APROBADO
    assert resultado.ponderacion_total == 100


@pytest.mark.parametrize(
    "pesos,bruto,definitiva,estado",
    [
        ((51, 49, 0), "2.949", "2.9", Estado.REPROBADO),
        ((50, 50, 0), "2.950", "3.0", Estado.APROBADO),
        ((49, 51, 0), "2.951", "3.0", Estado.APROBADO),
    ],
)
def test_frontera_redondeo(pesos, bruto, definitiva, estado):
    resultado = calcular_resultado(entrada(("2.9", "3.0", "0"), pesos))
    assert resultado.promedio_ponderado == Decimal(bruto)
    assert resultado.nota_definitiva == Decimal(definitiva)
    assert resultado.estado == estado


@pytest.mark.parametrize(
    "nota,estado", [("0", Estado.REPROBADO), ("5", Estado.APROBADO)]
)
def test_extremos_del_calculo(nota, estado):
    resultado = calcular_resultado(entrada((nota, nota, nota), (100, 0, 0)))
    assert resultado.nota_definitiva == Decimal(nota)
    assert resultado.estado == estado


def test_contexto_decimal_externo_no_redondea_el_calculo():
    with localcontext() as contexto:
        contexto.prec = 2
        resultado = calcular_resultado(entrada(("2.9", "3.0", "0"), (51, 49, 0)))
    assert resultado.promedio_ponderado == Decimal("2.949")
    assert resultado.nota_definitiva == Decimal("2.9")


def test_etiquetas_repetidas_permitidas():
    datos = entrada()
    for actividad in datos["actividades"]:
        actividad["nombre"] = "  Parcial  "
    assert [a.nombre for a in validar_entrada(datos)] == ["Parcial"] * 3


def test_estado_usa_definitiva():
    assert obtener_estado(Decimal("2.9")) == Estado.REPROBADO
    assert obtener_estado(Decimal("3.0")) == Estado.APROBADO
