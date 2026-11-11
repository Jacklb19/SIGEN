"""Contrato de respuestas correctas: salud, cálculo, redondeo y serialización."""

import re
from decimal import Decimal

import pytest
from ayudas_http import comprobar_json, tipo_contenido
from contrato_esperado import (
    CLAVES_RESULTADO,
    CUERPO_SALUD,
    EJEMPLO_GUIA,
    NOMBRE_MAX,
    RUTA_CALCULO,
    RUTA_SALUD,
    TOTAL_PESOS,
    cuerpo_bruto,
    peticion,
)

ENCABEZADO_JSON = {"Content-Type": "application/json"}


def calcular(cliente, datos):
    return comprobar_json(cliente.post(RUTA_CALCULO, json=datos), 200, "resultado")


# --- TP-23: salud -----------------------------------------------------------


def test_tp23_salud_responde_contrato_exacto(cliente):
    respuesta = cliente.get(RUTA_SALUD)

    cuerpo = comprobar_json(respuesta, 200, "salud")

    assert cuerpo == CUERPO_SALUD


# --- TP-21 / TP-24: ejemplo de la guía -----------------------------------------


def test_tp21_tp24_ejemplo_de_la_guia(cliente):
    cuerpo = calcular(cliente, EJEMPLO_GUIA)

    assert set(cuerpo) == CLAVES_RESULTADO
    assert cuerpo["promedio_ponderado"] == Decimal("3.4")
    assert cuerpo["nota_definitiva"] == Decimal("3.4")
    assert cuerpo["estado"] == "APROBADO"
    assert cuerpo["ponderacion_total"] == TOTAL_PESOS


def test_numeros_se_emiten_como_numeros_json_y_no_como_cadenas(cliente):
    respuesta = cliente.post(RUTA_CALCULO, json=EJEMPLO_GUIA)

    cuerpo = comprobar_json(respuesta, 200, "resultado")

    # Pydantic serializa Decimal como cadena por defecto; el contrato lo prohíbe.
    for clave in ("promedio_ponderado", "nota_definitiva"):
        assert isinstance(cuerpo[clave], Decimal), clave
        assert re.search(rf'"{clave}"\s*:\s*\d', respuesta.text), clave
    assert type(cuerpo["ponderacion_total"]) is int
    assert type(cuerpo["estado"]) is str


# --- TP-25: fronteras de redondeo HALF_UP del promedio bruto ----------------


@pytest.mark.parametrize(
    ("pesos", "bruto", "definitiva", "estado"),
    [
        pytest.param((51, 49, 0), "2.949", "2.9", "REPROBADO", id="TP-25a-2.949"),
        pytest.param((50, 50, 0), "2.95", "3.0", "APROBADO", id="TP-25b-2.950"),
        pytest.param((49, 51, 0), "2.951", "3.0", "APROBADO", id="TP-25c-2.951"),
    ],
)
def test_tp25_frontera_de_redondeo(cliente, pesos, bruto, definitiva, estado):
    datos = peticion(notas=(2.9, 3.0, 0.0), pesos=pesos)

    cuerpo = calcular(cliente, datos)

    # Comparación decimal exacta: comprueba que la serialización HTTP no
    # introduce redondeos ni artefactos binarios en el promedio bruto.
    assert cuerpo["promedio_ponderado"] == Decimal(bruto)
    assert cuerpo["nota_definitiva"] == Decimal(definitiva)
    assert cuerpo["estado"] == estado


# --- TP-08 / TP-09: el umbral se aplica a la definitiva ---------------------


@pytest.mark.parametrize(
    ("notas", "definitiva", "estado"),
    [
        pytest.param((2.9, 2.9, 2.9), "2.9", "REPROBADO", id="TP-08-definitiva-2.9"),
        pytest.param((3.0, 3.0, 3.0), "3.0", "APROBADO", id="TP-09-definitiva-3.0"),
        pytest.param((0.0, 0.0, 0.0), "0.0", "REPROBADO", id="minimo-0.0"),
        pytest.param((5.0, 5.0, 5.0), "5.0", "APROBADO", id="maximo-5.0"),
    ],
)
def test_tp08_tp09_umbral_de_aprobacion(cliente, notas, definitiva, estado):
    cuerpo = calcular(cliente, peticion(notas=notas))

    assert cuerpo["nota_definitiva"] == Decimal(definitiva)
    assert cuerpo["estado"] == estado


# --- TP-10, TP-13, TP-14: ponderaciones válidas -----------------------------


@pytest.mark.parametrize(
    ("pesos", "definitiva"),
    [
        pytest.param((30, 30, 40), "3.4", id="TP-10-30-30-40"),
        pytest.param((0, 50, 50), "3.3", id="TP-13-peso-cero"),
        pytest.param((100, 0, 0), "3.5", id="TP-14-100-0-0"),
        pytest.param((0, 0, 100), "4.0", id="TP-14-0-0-100"),
    ],
)
def test_ponderaciones_validas(cliente, pesos, definitiva):
    cuerpo = calcular(cliente, peticion(pesos=pesos))

    assert cuerpo["nota_definitiva"] == Decimal(definitiva)
    assert cuerpo["ponderacion_total"] == TOTAL_PESOS


# --- TP-01, 02, 04, 05: fronteras válidas de nota ----------------------------


@pytest.mark.parametrize(
    "nota", [0.0, 0.1, 4.9, 5.0], ids=["TP-01", "TP-02", "TP-05", "TP-04"]
)
def test_notas_frontera_validas(cliente, nota):
    calcular(cliente, peticion(notas=(nota, 2.5, 4.0)))


# --- TP-28: escrituras numéricas equivalentes --------------------------------


@pytest.mark.parametrize(
    ("token", "definitiva"),
    [
        ("3", "3.3"),  # bruto 3.25: HALF_UP
        ("3.0", "3.3"),
        ("3.50", "3.4"),
        ("35e-1", "3.4"),
        ("0.35E1", "3.4"),
        ("3.500000", "3.4"),
    ],
)
def test_tp28_escritura_numerica_equivalente(cliente, token, definitiva):
    respuesta = cliente.post(
        RUTA_CALCULO, content=cuerpo_bruto(nota=token), headers=ENCABEZADO_JSON
    )

    cuerpo = comprobar_json(respuesta, 200, "resultado")

    assert cuerpo["nota_definitiva"] == Decimal(definitiva)


# --- TP-29: nombres válidos ---------------------------------------------------


@pytest.mark.parametrize(
    "nombre",
    [
        pytest.param("A", id="1-caracter"),
        pytest.param("N" * NOMBRE_MAX, id="80-caracteres"),
        pytest.param("   " + "N" * NOMBRE_MAX + "  ", id="80-tras-recortar"),
        pytest.param("Á ñ ü — 📘", id="unicode"),
    ],
)
def test_tp29_nombres_validos(cliente, nombre):
    calcular(cliente, peticion(nombres=[nombre, "Parcial 2", "Proyecto"]))


def test_nombres_repetidos_son_validos(cliente):
    calcular(cliente, peticion(nombres=["Quiz", "Quiz", "Quiz"]))


# --- RF-08: simulaciones sin estado -----------------------------------------


def test_rf08_recalcular_no_conserva_estado_entre_peticiones(cliente):
    primero = calcular(cliente, peticion(notas=(1.0, 1.0, 1.0)))
    segundo = calcular(cliente, EJEMPLO_GUIA)
    tercero = calcular(cliente, peticion(notas=(1.0, 1.0, 1.0)))

    assert primero == tercero
    assert segundo["nota_definitiva"] == Decimal("3.4")


# --- Integración: rutas no interceptadas por el montaje estático ------------


def test_interfaz_y_documentacion_conviven_con_la_api(cliente):
    raiz = cliente.get("/")
    estatico = cliente.get("/static/app.js")
    documentacion = cliente.get("/openapi.json")

    assert raiz.status_code == 200
    assert tipo_contenido(raiz) == "text/html"
    assert estatico.status_code == 200
    assert documentacion.status_code == 200
    rutas = documentacion.json()["paths"]
    assert RUTA_SALUD in rutas
    assert set(rutas[RUTA_CALCULO]["post"]["responses"]) >= {"200", "400", "422", "500"}
