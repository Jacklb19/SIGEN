# Mantenimiento y regresión

## 1. Mantenimiento correctivo: demostración con defecto inducido

**El defecto es inducido a propósito para la demostración; no fue descubierto en producción.** Consiste en cambiar `nota <= NOTA_MAX` por `nota < NOTA_MAX` en `src/sigen/validators.py`, lo que rechazaría la nota válida 5.0 (TP-04, riesgo R1). El defecto **nunca** se deja en `main` ni en la rama de trabajo.

### Ejecución real registrada (10-nov-2026)

Se realizó en una copia aislada (`git worktree` temporal sobre el commit `9c382e7`), sin commits y eliminada al terminar:

| Paso | Acción | Resultado observado | Evidencia |
|---|---|---|---|
| 1 | Versión correcta con pruebas de frontera 5.0 | 255 aprobadas | [puerta_calidad.txt](evidencias/calidad/puerta_calidad.txt) |
| 2 | Inducir `nota < NOTA_MAX` | Diff de una línea | [01_defecto_inducido.txt](evidencias/mantenimiento/01_defecto_inducido.txt) |
| 3 | `python scripts/verificar_calidad.py` | **6 fallidas, 249 aprobadas; código de salida 1** | ídem |
| 4 | Corregir a `<=` | Diff vacío | [02_correccion.txt](evidencias/mantenimiento/02_correccion.txt) |
| 5 | `python scripts/verificar_calidad.py` | **255 aprobadas, líneas 203/203; código 0** | ídem |

Pruebas que detectaron el defecto: 2 independientes de contrato (`test_notas_frontera_validas[TP-04]` y `test_tp08_tp09_umbral_de_aprobacion[maximo-5.0]`, en `tests/contract/test_contrato_exito.py`) y 4 de Jose (`tests/api/test_api.py::test_notas_frontera_validas[5]`, `tests/unit/test_calculator.py::test_notas_validas[5]`, `test_notas_enteras[5]`, `test_extremos_del_calculo[5-APROBADO]`). La cobertura era del 100 % antes del defecto: lo que lo detecta son las aserciones de frontera, no la cobertura.

En las evidencias se sustituyeron las rutas locales por `<copia-aislada>`; la línea informativa de comando de esas dos capturas se normalizó a `$ python -m pytest …` (el script de entonces imprimía `$ -m pytest …`). El resto es la salida literal.

### Procedimiento para la sustentación (con Git y CI)

Requiere autorización expresa para crear commits en la rama de demostración y, si se quiere mostrar GitHub Actions, para publicarla. No hacer merge de la rama con el defecto.

```powershell
git switch -c demo/regresion-nota-maxima
# 1. Inducir el defecto en src/sigen/validators.py: "<= NOTA_MAX" -> "< NOTA_MAX"
git commit -am "demo: inducir defecto nota < 5.0 (defecto inducido)"
python scripts/verificar_calidad.py      # falla: TP-04 rechazada, código 1
# 2. Corregir a "<=" y repetir
git commit -am "fix(validacion): aceptar la nota maxima 5.0"
python scripts/verificar_calidad.py      # verde
git switch stefven/calidad               # o main; la rama demo no se fusiona
```

Mostrar `git log -p` de la rama demo y, si se publicó con autorización, la ejecución roja y luego verde de Actions. Al terminar, borrar la rama local (`git branch -D demo/regresion-nota-maxima`) si ya no se necesita.

## 2. Regresión continua

- `python scripts/verificar_calidad.py` ejecuta las 255 pruebas, incluidas las fronteras TP-01–TP-31, y aplica la puerta de líneas ≥ 80 %. La CI usa el mismo comando.
- Ante un defecto real: escribir primero una prueba que lo reproduzca (en rojo), corregir en el archivo de su responsable y conservar la prueba.
- Las pruebas de contrato no importan constantes del backend: un cambio de límites, rutas o códigos sin coordinar las hará fallar a propósito. Si el cambio está acordado, actualizar a la vez `docs/contrato_api.md`, `tests/contract/contrato_esperado.py` y `tests/contract/esquemas/`.

## 3. Actualizar dependencias

`pyproject.toml` declara rangos compatibles; los `requirements*.txt` son locks generados (no editarlos a mano):

```powershell
python -m pip install uv
python -m uv pip compile pyproject.toml --universal --python-version 3.11 --no-header -o requirements.txt
python -m uv pip compile pyproject.toml --extra dev --universal --python-version 3.11 --no-header -c requirements.txt -o requirements-dev.txt
```

`--universal` conserva los marcadores de plataforma (por ejemplo, `pywin32` solo en Windows) para que el mismo lock sirva en Windows y en la CI Linux. Tras regenerar: recrear el entorno, `python -m pip check` y `python scripts/verificar_calidad.py`. Pytest trata las advertencias como errores, de modo que una nueva deprecación se detecta al actualizar.

## 4. Otros tipos de mantenimiento (propuestas, no ejecutadas)

- **Preventivo:** unificar los nombres de excepciones (hallazgo N818 en `sigen.domain`) y los `parametrize` con tupla (PT006), coordinado con Jose.
- **Perfectivo:** mejorar mensajes de error en la interfaz con pruebas de Santiago.
- **Adaptativo:** política configurable de ponderaciones o de número de actividades, con nuevas pruebas de contrato.
