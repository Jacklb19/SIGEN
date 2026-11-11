"""Contrato de errores controlados: 422 por campo y 400 por regla de negocio.

Se comprueban códigos HTTP, códigos generales y pares (ruta, código) como
conjuntos, sin depender del orden de los errores ni del texto de los mensajes.
"""

import json

import pytest
from ayudas_http import comprobar_error
from contrato_esperado import (
    CAMPO_DESCONOCIDO,
    CANTIDAD,
    JSON_INVALIDO,
    LONGITUD,
    NOMBRE_MAX,
    PONDERACION_INVALIDA,
    PRECISION,
    RANGO,
    REQUERIDO,
    RUTA_ACTIVIDADES,
    RUTA_BODY,
    RUTA_CALCULO,
    RUTA_PESOS,
    SUMA_PESOS,
    TIPO,
    VALIDACION,
    cuerpo_bruto,
    peticion,
    ruta_actividad,
)

ENCABEZADO_JSON = {"Content-Type": "application/json"}
NOTA_0 = ruta_actividad(0, "nota")
PESO_0 = ruta_actividad(0, "peso")
NOMBRE_0 = ruta_actividad(0, "nombre")


def enviar(cliente, datos):
    return cliente.post(RUTA_CALCULO, json=datos)


def enviar_bruto(cliente, texto):
    return cliente.post(RUTA_CALCULO, content=texto, headers=ENCABEZADO_JSON)


def validar_422(respuesta):
    return comprobar_error(respuesta, 422, VALIDACION)


# --- RF-02: notas inválidas (TP-03, 06, 07, 16, 17, 18, 27) ------------------


@pytest.mark.parametrize(
    ("nota", "codigo"),
    [
        pytest.param(-0.1, RANGO, id="TP-03-negativa"),
        pytest.param(5.1, RANGO, id="TP-06-mayor-5"),
        pytest.param(3.55, PRECISION, id="TP-07-precision"),
        pytest.param(0.05, PRECISION, id="precision-cerca-del-minimo"),
        pytest.param(4.99, PRECISION, id="precision-cerca-del-maximo"),
        pytest.param("cuatro", TIPO, id="TP-16-texto"),
        pytest.param(None, TIPO, id="TP-17-null"),
        pytest.param(True, TIPO, id="TP-18-true"),
        pytest.param(False, TIPO, id="false"),
        pytest.param("4.5", TIPO, id="TP-27-cadena-numerica"),
        pytest.param([4.5], TIPO, id="lista"),
        pytest.param({"valor": 4.5}, TIPO, id="objeto"),
    ],
)
def test_nota_invalida(cliente, nota, codigo):
    datos = peticion(notas=(nota, 2.5, 4.0))

    errores = validar_422(enviar(cliente, datos))

    assert (NOTA_0, codigo) in errores


@pytest.mark.parametrize(
    ("token", "codigo"),
    [
        pytest.param("1e1000", RANGO, id="numero-json-enorme"),
        pytest.param("-0.1e0", RANGO, id="negativa-exponencial"),
        pytest.param(
            "3.5000000000000000000000000001", PRECISION, id="precision-oculta"
        ),
    ],
)
def test_nota_invalida_en_cuerpo_bruto(cliente, token, codigo):
    errores = validar_422(enviar_bruto(cliente, cuerpo_bruto(nota=token)))

    assert (NOTA_0, codigo) in errores


# --- RF-03: pesos inválidos (TP-15, TP-27) -----------------------------------


@pytest.mark.parametrize(
    ("peso", "codigo"),
    [
        pytest.param(-1, RANGO, id="negativo"),
        pytest.param(101, RANGO, id="TP-15-101"),
        pytest.param("30", TIPO, id="TP-27-cadena"),
        pytest.param(True, TIPO, id="TP-27-booleano"),
        pytest.param(None, TIPO, id="null"),
        pytest.param(30.5, TIPO, id="decimal"),
    ],
)
def test_peso_invalido(cliente, peso, codigo):
    errores = validar_422(enviar(cliente, peticion(pesos=(peso, 30, 40))))

    assert (PESO_0, codigo) in errores
    # Con errores de campo no se evalúa todavía la suma.
    assert all(codigo_campo != SUMA_PESOS for _, codigo_campo in errores)


@pytest.mark.parametrize("token", ["30.0", "3e1", "3.0E1"])
def test_tp27_peso_con_token_no_entero_se_rechaza(cliente, token):
    # 30.0 es un entero matemático, pero el contrato exige un token entero JSON.
    errores = validar_422(enviar_bruto(cliente, cuerpo_bruto(peso=token)))

    assert (PESO_0, TIPO) in errores


# --- RF-03: suma de pesos (TP-11, TP-12) -------------------------------------


@pytest.mark.parametrize(
    "pesos",
    [
        pytest.param((30, 30, 39), id="TP-11-suma-99"),
        pytest.param((30, 30, 41), id="TP-12-suma-101"),
        pytest.param((40, 30, 40), id="suma-110"),
        pytest.param((0, 0, 0), id="suma-0"),
        pytest.param((100, 100, 100), id="suma-300"),
    ],
)
def test_suma_de_pesos_distinta_de_100(cliente, pesos):
    errores = comprobar_error(
        enviar(cliente, peticion(pesos=pesos)), 400, PONDERACION_INVALIDA
    )

    assert errores == {(RUTA_PESOS, SUMA_PESOS)}


def test_errores_de_campo_tienen_precedencia_sobre_la_suma(cliente):
    # Suma 110 y además una nota fuera de rango: solo 422 de campo.
    datos = peticion(notas=(5.1, 2.5, 4.0), pesos=(40, 30, 40))

    errores = validar_422(enviar(cliente, datos))

    assert errores == {(NOTA_0, RANGO)}


# --- RF-01 / TP-29: nombres ---------------------------------------------------


@pytest.mark.parametrize(
    ("nombre", "codigo"),
    [
        pytest.param("", LONGITUD, id="vacio"),
        pytest.param("   ", LONGITUD, id="solo-blancos"),
        pytest.param("\t\n", LONGITUD, id="tabulador-y-salto"),
        pytest.param("N" * (NOMBRE_MAX + 1), LONGITUD, id="81-caracteres"),
        pytest.param(123, TIPO, id="numero"),
        pytest.param(None, TIPO, id="null"),
        pytest.param(["Parcial"], TIPO, id="lista"),
    ],
)
def test_tp29_nombre_invalido(cliente, nombre, codigo):
    datos = peticion(nombres=[nombre, "Parcial 2", "Proyecto"])

    errores = validar_422(enviar(cliente, datos))

    assert (NOMBRE_0, codigo) in errores


# --- RF-01 / TP-29: campos faltantes y adicionales ----------------------------


@pytest.mark.parametrize("campo", ["nombre", "nota", "peso"])
def test_tp29_campo_faltante(cliente, campo):
    datos = peticion()
    del datos["actividades"][1][campo]

    errores = validar_422(enviar(cliente, datos))

    assert (ruta_actividad(1, campo), REQUERIDO) in errores


def test_nota_requerida_aunque_el_peso_sea_cero(cliente):
    datos = peticion(pesos=(0, 60, 40))
    del datos["actividades"][0]["nota"]

    errores = validar_422(enviar(cliente, datos))

    assert errores == {(NOTA_0, REQUERIDO)}


def test_campo_adicional_en_actividad(cliente):
    datos = peticion()
    datos["actividades"][2]["comentario"] = "extra"

    errores = validar_422(enviar(cliente, datos))

    assert (ruta_actividad(2, "comentario"), CAMPO_DESCONOCIDO) in errores


def test_campo_adicional_en_la_raiz(cliente):
    datos = peticion()
    datos["estudiante"] = "Ficticio"

    errores = validar_422(enviar(cliente, datos))

    assert ("estudiante", CAMPO_DESCONOCIDO) in errores


def test_falta_la_clave_actividades(cliente):
    errores = validar_422(enviar(cliente, {}))

    assert (RUTA_ACTIVIDADES, REQUERIDO) in errores


def test_varios_errores_se_informan_juntos(cliente):
    datos = peticion(notas=(5.1, 3.55, "x"), pesos=(30, 101, 40))
    del datos["actividades"][2]["nombre"]

    errores = validar_422(enviar(cliente, datos))

    assert errores >= {
        (NOTA_0, RANGO),
        (ruta_actividad(1, "nota"), PRECISION),
        (ruta_actividad(2, "nota"), TIPO),
        (ruta_actividad(1, "peso"), RANGO),
        (ruta_actividad(2, "nombre"), REQUERIDO),
    }


# --- TP-19 / TP-20: cantidad de actividades ----------------------------------


@pytest.mark.parametrize(
    "cantidad",
    [
        pytest.param(0, id="ninguna"),
        pytest.param(2, id="TP-19-dos"),
        pytest.param(4, id="TP-20-cuatro"),
    ],
)
def test_cantidad_de_actividades(cliente, cantidad):
    actividad = {"nombre": "A", "nota": 3.0, "peso": 25}
    datos = {"actividades": [dict(actividad) for _ in range(cantidad)]}

    errores = validar_422(enviar(cliente, datos))

    assert (RUTA_ACTIVIDADES, CANTIDAD) in errores


@pytest.mark.parametrize(
    ("datos", "ruta"),
    [
        pytest.param({"actividades": "tres"}, RUTA_ACTIVIDADES, id="actividades-texto"),
        pytest.param({"actividades": None}, RUTA_ACTIVIDADES, id="actividades-null"),
        pytest.param([1, 2, 3], RUTA_BODY, id="raiz-lista"),
        pytest.param("texto", RUTA_BODY, id="raiz-cadena"),
        pytest.param(None, RUTA_BODY, id="raiz-null"),
    ],
)
def test_tipos_estructurales_incorrectos(cliente, datos, ruta):
    errores = validar_422(enviar_bruto(cliente, json.dumps(datos)))

    assert (ruta, TIPO) in errores


def test_actividad_que_no_es_objeto(cliente):
    datos = peticion()
    datos["actividades"][1] = "Parcial 2"

    errores = validar_422(enviar(cliente, datos))

    assert (ruta_actividad(1), TIPO) in errores


# --- TP-30: JSON mal formado y no finitos, enviados como cuerpo bruto ---------


@pytest.mark.parametrize(
    "texto",
    [
        pytest.param("", id="vacio"),
        pytest.param("{", id="incompleto"),
        pytest.param('{"actividades": [}', id="sintaxis"),
        pytest.param("{'actividades': []}", id="comillas-simples"),
        pytest.param('{"actividades": [],}', id="coma-final"),
        pytest.param(cuerpo_bruto(nota="NaN"), id="NaN"),
        pytest.param(cuerpo_bruto(nota="Infinity"), id="Infinity"),
        pytest.param(cuerpo_bruto(nota="-Infinity"), id="-Infinity"),
        pytest.param(cuerpo_bruto(peso="NaN"), id="peso-NaN"),
    ],
)
def test_tp30_cuerpo_no_json_valido(cliente, texto):
    # Ninguno de estos cuerpos es JSON estándar: se envían como bytes brutos.
    errores = validar_422(enviar_bruto(cliente, texto))

    assert errores == {(RUTA_BODY, JSON_INVALIDO)}


def test_tp30_bytes_que_no_son_utf8(cliente):
    respuesta = cliente.post(
        RUTA_CALCULO, content=b"\xff\xfe\x00", headers=ENCABEZADO_JSON
    )

    assert validar_422(respuesta) == {(RUTA_BODY, JSON_INVALIDO)}


# --- RNF-03: los errores no exponen datos de entrada ni trazas ----------------


def test_error_no_refleja_valores_de_la_peticion(cliente):
    marcador = "DatoPrivadoQueNoDebeVolver"
    datos = peticion(notas=(9.9, 2.5, 4.0), nombres=[marcador, "Parcial 2", "Proyecto"])
    datos["actividades"][1]["clave_extra"] = marcador

    respuesta = enviar(cliente, datos)

    validar_422(respuesta)
    assert marcador not in respuesta.text
    assert "9.9" not in respuesta.text
    assert "Traceback" not in respuesta.text
