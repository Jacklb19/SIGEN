"""TP-31: fallo inesperado controlado mediante sustitución temporal en pruebas.

No se modifica el código productivo: monkeypatch reemplaza durante la prueba
la función que usa el endpoint y se restaura automáticamente al terminar.
Siempre se ejecuta en proceso, aunque SIGEN_URL_BASE apunte a un servidor.
"""

import pytest
from ayudas_http import comprobar_error
from contrato_esperado import EJEMPLO_GUIA, ERROR_INTERNO, RUTA_CALCULO
from fastapi.testclient import TestClient

import sigen.api

DETALLE_SENSIBLE = "detalle-interno-sensible /ruta/secreta.py"


@pytest.fixture
def cliente_con_fallo(monkeypatch):
    def fallar(datos):
        raise RuntimeError(DETALLE_SENSIBLE)

    monkeypatch.setattr(sigen.api, "calcular_resultado", fallar)
    with TestClient(sigen.api.app, raise_server_exceptions=False) as cliente:
        yield cliente


def test_tp31_fallo_interno_responde_500_generico(cliente_con_fallo):
    respuesta = cliente_con_fallo.post(RUTA_CALCULO, json=EJEMPLO_GUIA)

    campos = comprobar_error(respuesta, 500, ERROR_INTERNO)

    assert campos == set()
    assert DETALLE_SENSIBLE not in respuesta.text
    assert "RuntimeError" not in respuesta.text
    assert "Parcial 1" not in respuesta.text


def test_la_sustitucion_es_temporal(cliente):
    # Tras las pruebas de fallo, la aplicación real vuelve a calcular.
    respuesta = cliente.post(RUTA_CALCULO, json=EJEMPLO_GUIA)

    assert respuesta.status_code == 200
