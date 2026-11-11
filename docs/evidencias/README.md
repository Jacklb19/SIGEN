# Evidencias

Salidas reales seleccionadas; los reportes generados (`htmlcov/`, `coverage.json`) se ignoran en Git y la CI los publica como artefacto. Las rutas locales del equipo se sustituyeron por `<repo>` o `<copia-aislada>`.

| Carpeta | Contenido | Explicación |
|---|---|---|
| `calidad/puerta_calidad.txt` | Salida de `python scripts/verificar_calidad.py` | [Reporte §3](../reporte_calidad.md#3-pruebas-y-cobertura) |
| `calidad/ruff.txt`, `calidad/bandit.txt` | Análisis estático de la puerta y exploración ampliada | [Reporte §4](../reporte_calidad.md#4-análisis-estático) |
| `carga/u{10,20,50}_*` | CSV y consola de Locust, corrida 2 (vigente) | [Reporte §6](../reporte_calidad.md#6-pruebas-de-carga) |
| `carga/corrida-1/` | Primera corrida, con 7 fallos HTTP 0 en el perfil de 20 usuarios | ídem |
| `mantenimiento/` | Defecto inducido `nota < 5.0` y corrección, en copia aislada | [Mantenimiento](../mantenimiento.md) |

GitHub Actions: ejecución `success` del workflow `CI` en `stefven/calidad`, commit `9d9a095`: https://github.com/Jacklb19/SIGEN/actions/runs/42962657637. El artefacto `cobertura` de esa ejecución contiene `coverage.json` y `htmlcov/`.
