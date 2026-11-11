"""Comando único de calidad: suite completa, cobertura y puerta de líneas.

Uso, desde la raíz del repositorio y con el entorno activado:

    python scripts/verificar_calidad.py

1. Ejecuta Pytest con cobertura de ``sigen`` (líneas y ramas) y reportes
   term-missing, HTML y JSON. Si la suite falla, propaga su código de salida.
2. Lee el reporte JSON y exige covered_lines / num_statements >= 0.80.
   Falla si el reporte no existe, está mal formado o no hay sentencias.
3. Informa las ramas cubiertas por separado. No existe umbral de ramas
   acordado, de modo que no se inventa uno.

``--cov-fail-under`` no se usa: con ``--cov-branch`` combina líneas y ramas
y no demuestra por sí solo el 80 % de líneas exigido (RNF-04).
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REPORTE_JSON = RAIZ / "coverage.json"
PAQUETE = "sigen"
UMBRAL_LINEAS = 0.80

COMANDO_PYTEST = [
    sys.executable,
    "-m",
    "pytest",
    f"--cov={PAQUETE}",
    "--cov-branch",
    "--cov-report=term-missing",
    "--cov-report=html",
    f"--cov-report=json:{REPORTE_JSON.name}",
]

# Códigos de salida propios (los de Pytest se propagan tal cual).
SALIDA_OK = 0
SALIDA_REPORTE_INVALIDO = 3
SALIDA_UMBRAL_INCUMPLIDO = 4


class ReporteInvalidoError(Exception):
    """El reporte de cobertura falta, está mal formado o no mide código."""


@dataclass(frozen=True)
class Cobertura:
    lineas_cubiertas: int
    sentencias: int
    ramas_cubiertas: int
    ramas: int

    @property
    def proporcion_lineas(self) -> float:
        return self.lineas_cubiertas / self.sentencias

    @property
    def proporcion_ramas(self) -> float | None:
        return self.ramas_cubiertas / self.ramas if self.ramas else None


def leer_cobertura(ruta: Path) -> Cobertura:
    """Extrae los totales del JSON de coverage.py sin usar percent_covered."""
    if not ruta.is_file():
        raise ReporteInvalidoError(f"No existe el reporte de cobertura: {ruta}")
    try:
        totales = json.loads(ruta.read_text(encoding="utf-8"))["totals"]
        cobertura = Cobertura(
            lineas_cubiertas=int(totales["covered_lines"]),
            sentencias=int(totales["num_statements"]),
            ramas_cubiertas=int(totales.get("covered_branches", 0)),
            ramas=int(totales.get("num_branches", 0)),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        mensaje = f"Reporte de cobertura mal formado: {error}"
        raise ReporteInvalidoError(mensaje) from error
    if cobertura.sentencias <= 0:
        raise ReporteInvalidoError("El reporte no contiene sentencias productivas.")
    if not 0 <= cobertura.lineas_cubiertas <= cobertura.sentencias:
        raise ReporteInvalidoError("Las líneas cubiertas no son coherentes.")
    return cobertura


def evaluar(cobertura: Cobertura, umbral: float = UMBRAL_LINEAS) -> bool:
    return cobertura.proporcion_lineas >= umbral


def describir(cobertura: Cobertura) -> str:
    lineas = (
        f"Líneas: {cobertura.lineas_cubiertas}/{cobertura.sentencias} "
        f"({cobertura.proporcion_lineas:.2%}); mínimo exigido {UMBRAL_LINEAS:.0%}."
    )
    if cobertura.proporcion_ramas is None:
        ramas = "Ramas: el reporte no contiene ramas medibles."
    else:
        ramas = (
            f"Ramas: {cobertura.ramas_cubiertas}/{cobertura.ramas} "
            f"({cobertura.proporcion_ramas:.2%}); informativo, sin umbral acordado."
        )
    return f"{lineas}\n{ramas}"


def main() -> int:
    # Salida legible también cuando se redirige (consola Windows, logs de CI).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # Un reporte de una ejecución anterior nunca debe aprobar esta.
    REPORTE_JSON.unlink(missing_ok=True)
    print("$ " + " ".join(COMANDO_PYTEST[1:]), flush=True)
    # Lista fija de argumentos, sin shell ni datos externos.
    resultado = subprocess.run(COMANDO_PYTEST, cwd=RAIZ, check=False)
    if resultado.returncode != 0:
        print(f"\nFALLO: Pytest terminó con código {resultado.returncode}.")
        return resultado.returncode

    try:
        cobertura = leer_cobertura(REPORTE_JSON)
    except ReporteInvalidoError as error:
        print(f"\nFALLO: {error}")
        return SALIDA_REPORTE_INVALIDO

    print("\n=== Puerta de calidad ===")
    print(describir(cobertura))
    if not evaluar(cobertura):
        print("FALLO: la cobertura de líneas es inferior al mínimo.")
        return SALIDA_UMBRAL_INCUMPLIDO
    print("APROBADO: suite en verde y cobertura de líneas suficiente.")
    return SALIDA_OK


if __name__ == "__main__":
    sys.exit(main())
