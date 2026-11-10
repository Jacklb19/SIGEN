"""Reglas compartidas del prototipo y rutas de integración."""

from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

NUM_ACTIVIDADES = 3
LONGITUD_NOMBRE_MIN = 1
LONGITUD_NOMBRE_MAX = 80
NOTA_MIN = Decimal("0.0")
NOTA_MAX = Decimal("5.0")
PASO_NOTA = Decimal("0.1")
NOTA_APROBACION = Decimal("3.0")
PESO_MIN = 0
PESO_MAX = 100
TOTAL_PESOS = 100
REDONDEO = ROUND_HALF_UP
PRECISION_CALCULO = 28

RUTA_CALCULO = "/api/v1/calcular"
RUTA_SALUD = "/health"
RUTA_ESTATICOS = "/static"
DIRECTORIO_WEB = Path(__file__).resolve().parents[2] / "web"
