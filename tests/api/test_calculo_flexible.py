import pytest
from fastapi.testclient import TestClient

from sigen.api import app


@pytest.mark.parametrize(
    ("escala", "cantidad", "nota", "estado"),
    [(5, 4, 4.0, "APROBADO"), (10, 5, 10, "APROBADO"), (10, 4, 5.9, "REPROBADO")],
)
def test_calculo_flexible(escala, cantidad, nota, estado):
    actividades = [
        {"nombre": f"Actividad {indice}", "nota": nota, "peso": 100 // cantidad}
        for indice in range(cantidad)
    ]
    with TestClient(app) as cliente:
        respuesta = cliente.post(
            "/api/v2/calcular", json={"escala": escala, "actividades": actividades}
        )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "promedio_ponderado": nota,
        "nota_definitiva": nota,
        "estado": estado,
        "ponderacion_total": 100,
    }


@pytest.mark.parametrize(
    ("escala", "cantidad", "nota", "codigo"),
    [
        (10, 2, 7, "CANTIDAD"),
        (10, 6, 7, "CANTIDAD"),
        (5, 4, 7, "RANGO"),
        (10, 4, 10.1, "RANGO"),
        (True, 4, 4, "ESCALA_INVALIDA"),
        (7, 4, 4, "ESCALA_INVALIDA"),
    ],
)
def test_calculo_flexible_rechaza_limites(escala, cantidad, nota, codigo):
    actividades = [
        {"nombre": "Actividad", "nota": nota, "peso": 25} for _ in range(cantidad)
    ]
    with TestClient(app) as cliente:
        respuesta = cliente.post(
            "/api/v2/calcular", json={"escala": escala, "actividades": actividades}
        )
    assert respuesta.status_code == 422
    assert codigo in {campo["codigo"] for campo in respuesta.json()["error"]["campos"]}


def test_umbral_de_escala_diez_se_aplica_despues_de_redondear():
    actividades = [
        {"nombre": "A", "nota": 5.9, "peso": 50},
        {"nombre": "B", "nota": 6.0, "peso": 50},
        {"nombre": "C", "nota": 0, "peso": 0},
    ]
    with TestClient(app) as cliente:
        respuesta = cliente.post(
            "/api/v2/calcular", json={"escala": 10, "actividades": actividades}
        )
    assert respuesta.status_code == 200
    assert respuesta.json()["promedio_ponderado"] == 5.95
    assert respuesta.json()["nota_definitiva"] == 6.0
    assert respuesta.json()["estado"] == "APROBADO"
