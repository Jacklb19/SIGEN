"""Prueba de carga local de SIGEN Lite con Locust.

Mezcla objetivo por pesos de tarea (aproximada, no exacta):
70 % cálculos válidos, 20 % salud y 10 % entradas inválidas esperadas.

Cada respuesta se comprueba con ``catch_response``: un 400/422 solo cuenta
como éxito cuando coincide con el código HTTP, el código de error y el par
(ruta, código) esperados para ese caso; cualquier otra respuesta es fallo.

Uso (servidor en otra terminal, sin --reload):

    python -m uvicorn sigen.api:app --host 127.0.0.1 --port 8000 --workers 1
    python -m locust -f locustfile.py --host http://127.0.0.1:8000 \
        --headless -u 10 -r 5 -t 60s --csv docs/evidencias/carga/u10
"""

import json
import random
from decimal import Decimal

from locust import HttpUser, between, task

from sigen.config import RUTA_CALCULO, RUTA_SALUD

# --- Parámetros de medición (documentados en docs/reporte_calidad.md) --------
ESPERA_MIN_S = 0.5
ESPERA_MAX_S = 1.5
PESO_CALCULO = 7
PESO_SALUD = 2
PESO_INVALIDO = 1

CUERPO_SALUD = {"status": "ok", "service": "sigen-lite"}
ENCABEZADO_JSON = {"Content-Type": "application/json"}


def _peticion(notas, pesos):
    nombres = ("Parcial 1", "Parcial 2", "Proyecto")
    return json.dumps(
        {
            "actividades": [
                {"nombre": n, "nota": nota, "peso": peso}
                for n, nota, peso in zip(nombres, notas, pesos, strict=True)
            ]
        }
    )


# (cuerpo, definitiva esperada, estado esperado)
CASOS_VALIDOS = [
    (_peticion((3.5, 2.5, 4.0), (30, 30, 40)), "3.4", "APROBADO"),
    (_peticion((2.9, 3.0, 0.0), (51, 49, 0)), "2.9", "REPROBADO"),
    (_peticion((2.9, 3.0, 0.0), (50, 50, 0)), "3.0", "APROBADO"),
    (_peticion((5.0, 5.0, 5.0), (100, 0, 0)), "5.0", "APROBADO"),
]

# (nombre, cuerpo bruto, HTTP, código general, ruta, código de campo)
CASOS_INVALIDOS = [
    (
        "nota 5.1",
        _peticion((5.1, 2.5, 4.0), (30, 30, 40)),
        422,
        "VALIDACION",
        "actividades.0.nota",
        "RANGO",
    ),
    (
        "suma 110",
        _peticion((3.5, 2.5, 4.0), (40, 30, 40)),
        400,
        "PONDERACION_INVALIDA",
        "actividades.pesos",
        "SUMA_PESOS",
    ),
    ("JSON roto", '{"actividades": [', 422, "VALIDACION", "body", "JSON_INVALIDO"),
]


def _json_decimal(respuesta):
    return json.loads(respuesta.content, parse_float=Decimal)


def _sin_respuesta(respuesta) -> str | None:
    """Describe un fallo de conexión (HTTP 0) con la excepción original."""
    if respuesta.status_code == 0:
        return f"Sin respuesta HTTP: {respuesta.error!r}"
    return None


def _es_json(respuesta) -> bool:
    return respuesta.headers.get("content-type", "").startswith("application/json")


class UsuarioSigen(HttpUser):
    wait_time = between(ESPERA_MIN_S, ESPERA_MAX_S)

    @task(PESO_CALCULO)
    def calcular_valido(self):
        cuerpo, definitiva, estado = random.choice(CASOS_VALIDOS)
        with self.client.post(
            RUTA_CALCULO,
            data=cuerpo,
            headers=ENCABEZADO_JSON,
            name="calcular valido",
            catch_response=True,
        ) as respuesta:
            if respuesta.status_code != 200 or not _es_json(respuesta):
                respuesta.failure(
                    _sin_respuesta(respuesta)
                    or f"HTTP {respuesta.status_code} inesperado"
                )
                return
            try:
                datos = _json_decimal(respuesta)
                correcto = (
                    datos["nota_definitiva"] == Decimal(definitiva)
                    and datos["estado"] == estado
                    and datos["ponderacion_total"] == 100
                )
            except (ValueError, KeyError, TypeError) as error:
                respuesta.failure(f"Cuerpo no conforme: {error}")
                return
            if correcto:
                respuesta.success()
            else:
                respuesta.failure("Resultado distinto del esperado")

    @task(PESO_SALUD)
    def salud(self):
        with self.client.get(
            RUTA_SALUD, name="salud", catch_response=True
        ) as respuesta:
            if (
                respuesta.status_code == 200
                and _es_json(respuesta)
                and respuesta.json() == CUERPO_SALUD
            ):
                respuesta.success()
            else:
                respuesta.failure(
                    _sin_respuesta(respuesta)
                    or f"Salud no conforme (HTTP {respuesta.status_code})"
                )

    @task(PESO_INVALIDO)
    def calcular_invalido(self):
        nombre, cuerpo, http, codigo, ruta, codigo_campo = random.choice(
            CASOS_INVALIDOS
        )
        with self.client.post(
            RUTA_CALCULO,
            data=cuerpo,
            headers=ENCABEZADO_JSON,
            name=f"invalido esperado: {nombre}",
            catch_response=True,
        ) as respuesta:
            if respuesta.status_code != http or not _es_json(respuesta):
                respuesta.failure(
                    _sin_respuesta(respuesta)
                    or f"Se esperaba HTTP {http} y llegó {respuesta.status_code}"
                )
                return
            try:
                error = respuesta.json()["error"]
                pares = {(c["ruta"], c["codigo"]) for c in error["campos"]}
                correcto = error["codigo"] == codigo and (ruta, codigo_campo) in pares
            except (ValueError, KeyError, TypeError) as fallo:
                respuesta.failure(f"Envoltorio no conforme: {fallo}")
                return
            if correcto:
                respuesta.success()
            else:
                respuesta.failure("Error distinto del esperado")
