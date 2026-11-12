"""Fixtures del contrato independiente.

Por defecto las pruebas usan la aplicación real ``sigen.api:app`` en proceso
(TestClient, HTTP sobre ASGI). Si se define ``SIGEN_URL_BASE`` (por ejemplo,
``http://127.0.0.1:8000``), se envían a un servidor Uvicorn ya arrancado; así
el mismo contrato se comprueba contra el proceso real.
"""

import os

import pytest
import requests
from fastapi.testclient import TestClient

from sigen.api import app

VARIABLE_URL_BASE = "SIGEN_URL_BASE"
TIEMPO_MAXIMO = 10


class ClienteRequests:
    def __init__(self, sesion: requests.Session, url_base: str):
        self.sesion = sesion
        self.url_base = url_base.rstrip("/")

    def get(self, ruta: str):
        return self.sesion.get(f"{self.url_base}{ruta}", timeout=TIEMPO_MAXIMO)

    def post(self, ruta: str, *, content=None, **opciones):
        return self.sesion.post(
            f"{self.url_base}{ruta}", data=content, timeout=TIEMPO_MAXIMO, **opciones
        )


@pytest.fixture(scope="session")
def cliente():
    url_base = os.environ.get(VARIABLE_URL_BASE)
    if url_base:
        with requests.Session() as sesion:
            yield ClienteRequests(sesion, url_base)
    else:
        with TestClient(app) as local:
            yield local
