"""Fixtures del contrato independiente.

Por defecto las pruebas usan la aplicación real ``sigen.api:app`` en proceso
(TestClient, HTTP sobre ASGI). Si se define ``SIGEN_URL_BASE`` (por ejemplo,
``http://127.0.0.1:8000``), se envían a un servidor Uvicorn ya arrancado; así
el mismo contrato se comprueba contra el proceso real.
"""

import os

import httpx2
import pytest
from fastapi.testclient import TestClient

from sigen.api import app

VARIABLE_URL_BASE = "SIGEN_URL_BASE"


@pytest.fixture(scope="session")
def cliente():
    url_base = os.environ.get(VARIABLE_URL_BASE)
    if url_base:
        with httpx2.Client(base_url=url_base, timeout=10) as remoto:
            yield remoto
    else:
        with TestClient(app) as local:
            yield local
