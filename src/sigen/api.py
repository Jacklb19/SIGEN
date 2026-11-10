"""Adaptador HTTP con decodificación decimal y errores públicos estables."""

import json
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from sigen.calculator import calcular_resultado
from sigen.config import DIRECTORIO_WEB, RUTA_CALCULO, RUTA_ESTATICOS, RUTA_SALUD
from sigen.domain import DatosInvalidos, ErrorCampo, PonderacionInvalida
from sigen.schemas import ENTRADA_SCHEMA, ERROR_SCHEMA, RESULTADO_SCHEMA


def _rechazar_constante(valor: str) -> None:
    raise ValueError("Constante no permitida en JSON.")


def _respuesta_error(error: DatosInvalidos) -> JSONResponse:
    return JSONResponse(
        status_code=400 if isinstance(error, PonderacionInvalida) else 422,
        content={
            "error": {
                "codigo": error.codigo,
                "mensaje": error.mensaje,
                "campos": [asdict(campo) for campo in error.campos],
            }
        },
    )


def crear_app(directorio_web: Path = DIRECTORIO_WEB) -> FastAPI:
    aplicacion = FastAPI(
        title="SIGEN Lite",
        version="0.1.0",
        description="Simulador académico. Redondeo HALF_UP asumido por el prototipo.",
    )

    @aplicacion.exception_handler(DatosInvalidos)
    async def error_datos(request: Request, error: DatosInvalidos) -> JSONResponse:
        return _respuesta_error(error)

    @aplicacion.exception_handler(Exception)
    async def error_inesperado(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "codigo": "ERROR_INTERNO",
                    "mensaje": "No fue posible completar la operación.",
                    "campos": [],
                }
            },
        )

    @aplicacion.get(RUTA_SALUD, summary="Comprobar disponibilidad")
    async def salud() -> dict[str, str]:
        return {"status": "ok", "service": "sigen-lite"}

    @aplicacion.post(
        RUTA_CALCULO,
        summary="Calcular la definitiva de tres actividades",
        response_class=JSONResponse,
        responses={
            200: {"content": {"application/json": {"schema": RESULTADO_SCHEMA}}},
            **{
                codigo: {
                    "description": descripcion,
                    "content": {"application/json": {"schema": ERROR_SCHEMA}},
                }
                for codigo, descripcion in (
                    (400, "Los porcentajes no suman 100."),
                    (422, "JSON o campos inválidos."),
                    (500, "Fallo inesperado del servidor."),
                )
            },
        },
        openapi_extra={
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": ENTRADA_SCHEMA}},
            }
        },
    )
    async def calcular(request: Request) -> JSONResponse:
        try:
            datos = json.loads(
                await request.body(),
                parse_float=Decimal,
                parse_constant=_rechazar_constante,
            )
        except (
            ValueError,
            UnicodeDecodeError,
            InvalidOperation,
            RecursionError,
        ) as error:
            raise DatosInvalidos(
                [ErrorCampo("body", "JSON_INVALIDO", "El cuerpo no es JSON válido.")]
            ) from error
        resultado = calcular_resultado(datos)
        # El cálculo ya terminó en Decimal. Solo la representación HTTP usa float:
        # las entradas permitidas producen promedios de hasta tres decimales.
        return JSONResponse(
            content={
                "promedio_ponderado": float(resultado.promedio_ponderado),
                "nota_definitiva": float(resultado.nota_definitiva),
                "estado": resultado.estado.value,
                "ponderacion_total": resultado.ponderacion_total,
            }
        )

    @aplicacion.get("/", include_in_schema=False)
    async def interfaz() -> FileResponse:
        pagina = directorio_web / "index.html"
        if not pagina.is_file():
            raise HTTPException(
                status_code=404, detail="La interfaz aún no está disponible."
            )
        return FileResponse(pagina)

    # La API arranca sin los archivos de Santiago. Reiniciar al agregarlos.
    if directorio_web.is_dir():
        aplicacion.mount(
            RUTA_ESTATICOS, StaticFiles(directory=directorio_web), name="static"
        )
    return aplicacion


app = crear_app()
