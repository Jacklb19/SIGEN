"""Integración HTTP del frente de Jose; no sustituye el contrato independiente."""

import copy
import json
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

import sigen.api as modulo_api
from sigen.api import crear_app

RUTA = "/api/v1/calcular"


@pytest.fixture
def datos():
    return {
        "actividades": [
            {"nombre": "Parcial 1", "nota": 3.5, "peso": 30},
            {"nombre": "Parcial 2", "nota": 2.5, "peso": 30},
            {"nombre": "Proyecto", "nota": 4.0, "peso": 40},
        ]
    }


@pytest.fixture
def cliente(tmp_path):
    with TestClient(crear_app(tmp_path / "web")) as cliente:
        yield cliente


def comprobar_error(respuesta, status, codigo, ruta, campo_codigo):
    assert respuesta.status_code == status
    assert respuesta.headers["content-type"] == "application/json"
    error = respuesta.json()["error"]
    assert error["codigo"] == codigo
    assert any(
        campo["ruta"] == ruta and campo["codigo"] == campo_codigo
        for campo in error["campos"]
    )


def test_salud(cliente):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok", "service": "sigen-lite"}


def test_calculo_ejemplo(cliente, datos):
    respuesta = cliente.post(RUTA, json=datos)
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/json"
    assert respuesta.json() == {
        "promedio_ponderado": 3.4,
        "nota_definitiva": 3.4,
        "estado": "APROBADO",
        "ponderacion_total": 100,
    }
    assert type(respuesta.json()["nota_definitiva"]) is float
    assert type(respuesta.json()["ponderacion_total"]) is int


@pytest.mark.parametrize(
    "nota,codigo",
    [
        ("4.5", "TIPO"),
        (True, "TIPO"),
        (None, "TIPO"),
        (-0.1, "RANGO"),
        (5.1, "RANGO"),
        (3.55, "PRECISION"),
        ([], "TIPO"),
        ({}, "TIPO"),
    ],
)
def test_notas_invalidas(cliente, datos, nota, codigo):
    datos["actividades"][0]["nota"] = nota
    comprobar_error(
        cliente.post(RUTA, json=datos), 422, "VALIDACION", "actividades.0.nota", codigo
    )


@pytest.mark.parametrize("nota", [0, 0.1, 4.9, 5])
def test_notas_frontera_validas(cliente, datos, nota):
    datos["actividades"][0]["nota"] = nota
    assert cliente.post(RUTA, json=datos).status_code == 200


@pytest.mark.parametrize("token", ["3.50", "35e-1", "3", "3.0"])
def test_escritura_numerica_equivalente(cliente, datos, token):
    cuerpo = json.dumps(datos).replace('"nota": 3.5', f'"nota": {token}', 1)
    assert cliente.post(RUTA, content=cuerpo).status_code == 200


def test_no_pierde_precision_al_decodificar(cliente, datos):
    # Convertir primero a float ocultaría esta precisión no admitida.
    cuerpo = json.dumps(datos).replace("3.5", "3.5000000000000000000000000001", 1)
    comprobar_error(
        cliente.post(RUTA, content=cuerpo),
        422,
        "VALIDACION",
        "actividades.0.nota",
        "PRECISION",
    )


@pytest.mark.parametrize(
    "peso,codigo",
    [
        (30.0, "TIPO"),
        ("30", "TIPO"),
        (True, "TIPO"),
        (None, "TIPO"),
        (-1, "RANGO"),
        (101, "RANGO"),
        (30.1, "TIPO"),
    ],
)
def test_pesos_invalidos(cliente, datos, peso, codigo):
    datos["actividades"][0]["peso"] = peso
    comprobar_error(
        cliente.post(RUTA, json=datos), 422, "VALIDACION", "actividades.0.peso", codigo
    )


@pytest.mark.parametrize("pesos", [(30, 30, 39), (30, 30, 41), (30, 30, 50)])
def test_suma_invalida(cliente, datos, pesos):
    for actividad, peso in zip(datos["actividades"], pesos, strict=True):
        actividad["peso"] = peso
    comprobar_error(
        cliente.post(RUTA, json=datos),
        400,
        "PONDERACION_INVALIDA",
        "actividades.pesos",
        "SUMA_PESOS",
    )


def test_error_de_campo_precede_a_suma(cliente, datos):
    datos["actividades"][0]["nota"] = "incorrecta"
    datos["actividades"][1]["peso"] = 50
    respuesta = cliente.post(RUTA, json=datos)
    assert respuesta.status_code == 422
    assert all(c["codigo"] != "SUMA_PESOS" for c in respuesta.json()["error"]["campos"])


@pytest.mark.parametrize("cantidad", [0, 2, 4])
def test_cantidad_actividades(cliente, datos, cantidad):
    datos["actividades"] = (datos["actividades"] * 2)[:cantidad]
    comprobar_error(
        cliente.post(RUTA, json=datos), 422, "VALIDACION", "actividades", "CANTIDAD"
    )


@pytest.mark.parametrize("valor", [None, True, 5, "texto", [], {}])
def test_objeto_raiz_o_campo_actividades_invalido(cliente, valor):
    cuerpo = json.dumps(valor)
    respuesta = cliente.post(RUTA, content=cuerpo)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"


@pytest.mark.parametrize("valor", [None, {}, "texto", True])
def test_actividades_debe_ser_lista(cliente, valor):
    comprobar_error(
        cliente.post(RUTA, json={"actividades": valor}),
        422,
        "VALIDACION",
        "actividades",
        "TIPO",
    )


def test_actividad_debe_ser_objeto(cliente, datos):
    datos["actividades"][0] = None
    comprobar_error(
        cliente.post(RUTA, json=datos), 422, "VALIDACION", "actividades.0", "TIPO"
    )


@pytest.mark.parametrize("campo", ["nombre", "nota", "peso"])
def test_campos_requeridos_incluso_peso_cero(cliente, datos, campo):
    for actividad, peso in zip(datos["actividades"], [100, 0, 0], strict=True):
        actividad["peso"] = peso
    del datos["actividades"][1][campo]
    comprobar_error(
        cliente.post(RUTA, json=datos),
        422,
        "VALIDACION",
        f"actividades.1.{campo}",
        "REQUERIDO",
    )


@pytest.mark.parametrize("raiz", [True, False])
def test_claves_desconocidas(cliente, datos, raiz):
    destino = datos if raiz else datos["actividades"][0]
    destino["extra"] = "no publicar este valor"
    ruta = "extra" if raiz else "actividades.0.extra"
    respuesta = cliente.post(RUTA, json=datos)
    comprobar_error(respuesta, 422, "VALIDACION", ruta, "CAMPO_DESCONOCIDO")
    assert "no publicar este valor" not in respuesta.text


@pytest.mark.parametrize(
    "nombre,codigo",
    [
        ("", "LONGITUD"),
        ("  ", "LONGITUD"),
        ("A" * 81, "LONGITUD"),
        (None, "TIPO"),
        (True, "TIPO"),
    ],
)
def test_nombres_invalidos(cliente, datos, nombre, codigo):
    datos["actividades"][0]["nombre"] = nombre
    comprobar_error(
        cliente.post(RUTA, json=datos),
        422,
        "VALIDACION",
        "actividades.0.nombre",
        codigo,
    )


@pytest.mark.parametrize("nombre", ["A", "A" * 80, "  Proyecto  "])
def test_nombres_validos(cliente, datos, nombre):
    datos["actividades"][0]["nombre"] = nombre
    assert cliente.post(RUTA, json=datos).status_code == 200


@pytest.mark.parametrize(
    "cuerpo",
    [
        b"",
        b"{",
        b"\xff",
        b'{"actividades":NaN}',
        b'{"actividades":Infinity}',
        b'{"actividades":-Infinity}',
    ],
)
def test_json_invalido(cliente, cuerpo):
    comprobar_error(
        cliente.post(RUTA, content=cuerpo), 422, "VALIDACION", "body", "JSON_INVALIDO"
    )


@pytest.mark.parametrize(
    "pesos,bruto,definitiva,estado",
    [
        ([51, 49, 0], "2.949", "2.9", "REPROBADO"),
        ([50, 50, 0], "2.950", "3.0", "APROBADO"),
        ([49, 51, 0], "2.951", "3.0", "APROBADO"),
    ],
)
def test_redondeo_real_http(cliente, datos, pesos, bruto, definitiva, estado):
    for actividad, nota, peso in zip(
        datos["actividades"], [2.9, 3.0, 0], pesos, strict=True
    ):
        actividad.update(nota=nota, peso=peso)
    respuesta = cliente.post(RUTA, json=datos)
    assert respuesta.status_code == 200
    resultado = json.loads(respuesta.text, parse_float=Decimal)
    assert resultado["promedio_ponderado"] == Decimal(bruto)
    assert resultado["nota_definitiva"] == Decimal(definitiva)
    assert resultado["estado"] == estado


def test_fallo_inesperado_no_expone_detalles(cliente, datos, monkeypatch):
    def fallo(datos):
        raise RuntimeError("detalle privado que no debe publicarse")

    monkeypatch.setattr(modulo_api, "calcular_resultado", fallo)
    with TestClient(cliente.app, raise_server_exceptions=False) as cliente_fallo:
        respuesta = cliente_fallo.post(RUTA, json=datos)
    assert respuesta.status_code == 500
    assert respuesta.json() == {
        "error": {
            "codigo": "ERROR_INTERNO",
            "mensaje": "No fue posible completar la operación.",
            "campos": [],
        }
    }
    assert "privado" not in respuesta.text
    assert "RuntimeError" not in respuesta.text


def test_api_funciona_sin_interfaz(cliente):
    assert cliente.get("/").status_code == 404
    assert cliente.get("/static/styles.css").status_code == 404
    assert cliente.get("/docs").status_code == 200
    assert cliente.get("/health").status_code == 200


def test_montaje_interfaz_no_intercepta_api(tmp_path, datos):
    (tmp_path / "index.html").write_text("<h1>Fixture de prueba</h1>", encoding="utf-8")
    (tmp_path / "styles.css").write_text("body { color: blue; }", encoding="utf-8")
    with TestClient(crear_app(tmp_path)) as cliente:
        assert cliente.get("/").status_code == 200
        assert cliente.get("/static/styles.css").status_code == 200
        assert cliente.get("/health").status_code == 200
        assert cliente.get("/docs").status_code == 200
        assert cliente.post(RUTA, json=datos).status_code == 200
        assert cliente.get("/static/../api.py").status_code == 404


def test_openapi_describe_esquemas_reales(cliente, datos):
    documento = cliente.get("/openapi.json").json()
    operacion = documento["paths"][RUTA]["post"]
    esquema_entrada = operacion["requestBody"]["content"]["application/json"]["schema"]
    Draft202012Validator.check_schema(esquema_entrada)
    # Decimal evita los falsos negativos de multipleOf=0.1 en algunos floats.
    esquema_decimal = json.loads(json.dumps(esquema_entrada), parse_float=Decimal)
    datos_decimal = json.loads(json.dumps(datos), parse_float=Decimal)
    Draft202012Validator(esquema_decimal).validate(datos_decimal)
    for codigo, respuesta in [
        ("200", cliente.post(RUTA, json=datos)),
        ("422", cliente.post(RUTA, json={})),
        (
            "400",
            cliente.post(
                RUTA,
                json={
                    "actividades": [
                        dict(a, peso=0) for a in copy.deepcopy(datos["actividades"])
                    ]
                },
            ),
        ),
    ]:
        esquema = operacion["responses"][codigo]["content"]["application/json"][
            "schema"
        ]
        Draft202012Validator.check_schema(esquema)
        esquema = json.loads(json.dumps(esquema), parse_float=Decimal)
        cuerpo = json.loads(respuesta.text, parse_float=Decimal)
        Draft202012Validator(esquema).validate(cuerpo)
