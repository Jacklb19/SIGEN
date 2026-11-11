"""Pruebas de la puerta de calidad: lectura del reporte y umbral de líneas.

Se prueban las funciones puras; main() no se invoca aquí porque ejecuta la
propia suite y provocaría una recursión.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

RUTA_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "verificar_calidad.py"
_spec = importlib.util.spec_from_file_location("verificar_calidad", RUTA_SCRIPT)
vc = importlib.util.module_from_spec(_spec)
# dataclasses necesita el módulo registrado antes de ejecutarlo.
sys.modules[_spec.name] = vc
_spec.loader.exec_module(vc)


def escribir_reporte(tmp_path, totales):
    ruta = tmp_path / "coverage.json"
    ruta.write_text(json.dumps({"totals": totales}), encoding="utf-8")
    return ruta


def totales(lineas, sentencias, ramas_cubiertas=0, ramas=0):
    return {
        "covered_lines": lineas,
        "num_statements": sentencias,
        "covered_branches": ramas_cubiertas,
        "num_branches": ramas,
        # Valor combinado engañoso: la puerta no debe usarlo.
        "percent_covered": 99.0,
    }


@pytest.mark.parametrize(
    ("lineas", "sentencias", "aprueba"),
    [(80, 100, True), (79, 100, False), (100, 100, True), (0, 10, False)],
)
def test_umbral_de_lineas_en_la_frontera(tmp_path, lineas, sentencias, aprueba):
    ruta = escribir_reporte(tmp_path, totales(lineas, sentencias))

    cobertura = vc.leer_cobertura(ruta)

    assert vc.evaluar(cobertura) is aprueba


def test_la_puerta_ignora_el_porcentaje_combinado(tmp_path):
    # 79 % de líneas con 100 % de ramas da un combinado mayor al 80 %.
    ruta = escribir_reporte(tmp_path, totales(79, 100, 50, 50))

    cobertura = vc.leer_cobertura(ruta)

    assert vc.UMBRAL_LINEAS < (79 + 50) / (100 + 50)
    assert vc.evaluar(cobertura) is False


def test_reporte_ausente_falla(tmp_path):
    with pytest.raises(vc.ReporteInvalido, match="No existe"):
        vc.leer_cobertura(tmp_path / "coverage.json")


def test_cero_sentencias_falla(tmp_path):
    ruta = escribir_reporte(tmp_path, totales(0, 0))

    with pytest.raises(vc.ReporteInvalido, match="sentencias"):
        vc.leer_cobertura(ruta)


@pytest.mark.parametrize(
    "contenido",
    ["no es json", json.dumps({}), json.dumps({"totals": {"covered_lines": 5}})],
)
def test_reporte_mal_formado_falla(tmp_path, contenido):
    ruta = tmp_path / "coverage.json"
    ruta.write_text(contenido, encoding="utf-8")

    with pytest.raises(vc.ReporteInvalido, match="mal formado"):
        vc.leer_cobertura(ruta)


def test_lineas_incoherentes_fallan(tmp_path):
    ruta = escribir_reporte(tmp_path, totales(11, 10))

    with pytest.raises(vc.ReporteInvalido, match="coherentes"):
        vc.leer_cobertura(ruta)


def test_describe_lineas_y_ramas_por_separado():
    cobertura = vc.Cobertura(203, 203, 49, 50)

    texto = vc.describir(cobertura)

    assert "Líneas: 203/203 (100.00%)" in texto
    assert "Ramas: 49/50 (98.00%)" in texto
    assert "sin umbral" in texto


def test_describe_reporte_sin_ramas():
    assert "no contiene ramas" in vc.describir(vc.Cobertura(5, 5, 0, 0))


def test_main_propaga_el_fallo_de_pytest(monkeypatch, tmp_path):
    class Resultado:
        returncode = 1

    monkeypatch.setattr(vc, "REPORTE_JSON", tmp_path / "coverage.json")
    monkeypatch.setattr(vc.subprocess, "run", lambda *a, **k: Resultado())

    assert vc.main() == 1


def test_main_falla_si_pytest_no_genera_reporte(monkeypatch, tmp_path):
    class Resultado:
        returncode = 0

    monkeypatch.setattr(vc, "REPORTE_JSON", tmp_path / "coverage.json")
    monkeypatch.setattr(vc.subprocess, "run", lambda *a, **k: Resultado())

    assert vc.main() == vc.SALIDA_REPORTE_INVALIDO


@pytest.mark.parametrize(
    ("lineas", "esperado"), [(79, "SALIDA_UMBRAL_INCUMPLIDO"), (80, "SALIDA_OK")]
)
def test_main_aplica_la_puerta(monkeypatch, tmp_path, lineas, esperado):
    reporte = tmp_path / "coverage.json"

    class Resultado:
        returncode = 0

    def ejecutar_pytest(*args, **kwargs):
        # Simula el reporte que pytest-cov escribiría tras la limpieza previa.
        escribir_reporte(tmp_path, totales(lineas, 100))
        return Resultado()

    monkeypatch.setattr(vc, "REPORTE_JSON", reporte)
    monkeypatch.setattr(vc.subprocess, "run", ejecutar_pytest)

    assert vc.main() == getattr(vc, esperado)


def test_main_elimina_un_reporte_anterior(monkeypatch, tmp_path):
    reporte = escribir_reporte(tmp_path, totales(100, 100))

    class Resultado:
        returncode = 0

    monkeypatch.setattr(vc, "REPORTE_JSON", reporte)
    monkeypatch.setattr(vc.subprocess, "run", lambda *a, **k: Resultado())

    # El reporte viejo aprobaría; como se borra antes, la puerta falla.
    assert vc.main() == vc.SALIDA_REPORTE_INVALIDO
