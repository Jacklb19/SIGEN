"""Adaptador HTTP con decodificación decimal y errores públicos estables."""

import json
import logging
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from sigen.calculator import calcular_resultado, calcular_resultado_flexible
from sigen.config import (
    DIRECTORIO_WEB,
    RUTA_CALCULO,
    RUTA_CALCULO_FLEXIBLE,
    RUTA_ESTATICOS,
    RUTA_SALUD,
)
from sigen.domain import DatosInvalidos, ErrorCampo, PonderacionInvalida
from sigen.schemas import (
    ENTRADA_FLEXIBLE_SCHEMA,
    ENTRADA_SCHEMA,
    ERROR_SCHEMA,
    RESULTADO_FLEXIBLE_SCHEMA,
    RESULTADO_SCHEMA,
)

REGISTRO_HTTP = logging.getLogger("uvicorn.error")


def _documentar_calculo(entrada, resultado):
    return {
        "response_class": JSONResponse,
        "responses": {
            200: {"content": {"application/json": {"schema": resultado}}},
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
        "openapi_extra": {
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": entrada}},
            }
        },
    }


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

    @aplicacion.middleware("http")
    async def medir_solicitud(request: Request, call_next):
        inicio = perf_counter()
        estado = 500
        try:
            respuesta = await call_next(request)
            estado = respuesta.status_code
            duracion_ms = (perf_counter() - inicio) * 1000
            respuesta.headers["Server-Timing"] = f"app;dur={duracion_ms:.2f}"
            return respuesta
        finally:
            ruta = getattr(request.scope.get("route"), "path", "sin_ruta")
            REGISTRO_HTTP.log(
                logging.ERROR if estado >= 500 else logging.INFO,
                "%s %s estado=%d duracion_ms=%.2f",
                request.method,
                ruta,
                estado,
                (perf_counter() - inicio) * 1000,
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
        **_documentar_calculo(ENTRADA_SCHEMA, RESULTADO_SCHEMA),
    )
    async def calcular(request: Request) -> JSONResponse:
        return await resolver_calculo(request, calcular_resultado)

    @aplicacion.post(
        RUTA_CALCULO_FLEXIBLE,
        summary="Calcular entre tres y cinco actividades en escala de 5 o 10",
        **_documentar_calculo(ENTRADA_FLEXIBLE_SCHEMA, RESULTADO_FLEXIBLE_SCHEMA),
    )
    async def calcular_flexible(request: Request) -> JSONResponse:
        return await resolver_calculo(request, calcular_resultado_flexible)

    async def resolver_calculo(request: Request, motor) -> JSONResponse:
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
        resultado = motor(datos)
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
