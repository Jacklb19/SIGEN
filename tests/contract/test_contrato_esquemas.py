"""Esquemas JSON del contrato y límites conocidos de JSON Schema.

Los esquemas viven en tests/contract/esquemas y declaran Draft 2020-12. Son
independientes de sigen.schemas: describen lo acordado en la guía §5.
"""

import json
from decimal import Decimal

import pytest
from ayudas_http import VALIDADORES, comprobar_error
from contrato_esperado import (
    EJEMPLO_GUIA,
    NOMBRE_MAX,
    PONDERACION_INVALIDA,
    RUTA_CALCULO,
    TIPO,
    VALIDACION,
    cargar_esquema,
    como_json_decimal,
    cuerpo_bruto,
    peticion,
    ruta_actividad,
)
from jsonschema import Draft202012Validator

DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"
NOMBRES = ("salud", "entrada", "resultado", "error")


@pytest.mark.parametrize("nombre", NOMBRES)
def test_esquema_declara_version_y_es_valido(nombre):
    esquema = cargar_esquema(nombre)

    assert esquema["$schema"] == DRAFT_2020_12
    Draft202012Validator.check_schema(esquema)


@pytest.mark.parametrize("nombre", ["entrada", "resultado", "error"])
def test_esquemas_rechazan_propiedades_adicionales(nombre):
    assert cargar_esquema(nombre)["additionalProperties"] is False


def test_ejemplo_de_la_guia_cumple_el_esquema_de_entrada():
    assert VALIDADORES["entrada"].is_valid(como_json_decimal(EJEMPLO_GUIA))


@pytest.mark.parametrize("nota", ["0.3", "2.3", "4.9", "0.1"])
def test_multipleof_exacto_al_decodificar_con_decimal(nota):
    # Con floats binarios, 0.3 % 0.1 != 0 y el verificador daría un falso
    # negativo. Esquema e instancia se decodifican con Decimal.
    datos = json.loads(cuerpo_bruto(nota=nota), parse_float=Decimal)

    assert VALIDADORES["entrada"].is_valid(datos)


def test_esquema_no_basta_para_la_suma_de_pesos(cliente):
    datos = peticion(pesos=(40, 30, 40))

    # El esquema acepta la estructura, pero la regla de negocio la rechaza.
    assert VALIDADORES["entrada"].is_valid(como_json_decimal(datos))
    comprobar_error(cliente.post(RUTA_CALCULO, json=datos), 400, PONDERACION_INVALIDA)


def test_esquema_con_floats_no_distingue_30_de_30_0(cliente):
    texto = cuerpo_bruto(peso="30.0")
    esquema_float = json.loads(json.dumps(cargar_esquema("entrada"), default=float))

    # Decodificado como float, JSON Schema trata 30.0 como entero válido...
    assert Draft202012Validator(esquema_float).is_valid(json.loads(texto))
    # ...pero el servidor exige el token entero JSON y lo rechaza.
    respuesta = cliente.post(
        RUTA_CALCULO, content=texto, headers={"Content-Type": "application/json"}
    )
    errores = comprobar_error(respuesta, 422, VALIDACION)
    assert (ruta_actividad(0, "peso"), TIPO) in errores


def test_esquema_no_aplica_la_longitud_tras_recortar():
    # 81 caracteres útiles: el esquema no lo detecta; lo hace el servidor
    # (cubierto en test_contrato_errores::test_tp29_nombre_invalido).
    datos = peticion(nombres=["N" * (NOMBRE_MAX + 1), "B", "C"])

    assert VALIDADORES["entrada"].is_valid(como_json_decimal(datos))


@pytest.mark.parametrize(
    ("instancia", "valido"),
    [
        (
            {
                "promedio_ponderado": 3.4,
                "nota_definitiva": 3.4,
                "estado": "APROBADO",
                "ponderacion_total": 100,
            },
            True,
        ),
        (
            {
                "promedio_ponderado": "3.4",
                "nota_definitiva": 3.4,
                "estado": "APROBADO",
                "ponderacion_total": 100,
            },
            False,
        ),
        (
            {"promedio_ponderado": 3.4, "nota_definitiva": 3.4, "estado": "APROBADO"},
            False,
        ),
        (
            {
                "promedio_ponderado": 3.4,
                "nota_definitiva": 3.4,
                "estado": "OTRO",
                "ponderacion_total": 100,
            },
            False,
        ),
        (
            {
                "promedio_ponderado": 3.4,
                "nota_definitiva": 3.4,
                "estado": "APROBADO",
                "ponderacion_total": 100,
                "x": 1,
            },
            False,
        ),
    ],
    ids=[
        "valido",
        "numero-como-cadena",
        "clave-faltante",
        "estado-desconocido",
        "clave-extra",
    ],
)
def test_esquema_de_resultado_detecta_desviaciones(instancia, valido):
    # Prueba del propio oráculo: el esquema rechaza las desviaciones típicas.
    assert VALIDADORES["resultado"].is_valid(como_json_decimal(instancia)) is valido
