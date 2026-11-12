# Desplegar SIGEN Lite en Vercel

El repositorio público `Jacklb19/SIGEN` contiene una aplicación FastAPI con su interfaz en el mismo origen. Vercel reconoce `src/app.py` como entrada. `.python-version` fija Python 3.12 y los archivos web están incluidos en el paquete.

1. Iniciar sesión en Vercel con la cuenta que tiene acceso al repositorio. Usar el plan **Hobby** para la demostración académica, sujeto a las condiciones y cuotas del plan.
2. En el panel, elegir **Add New → Project** e importar `Jacklb19/SIGEN` desde GitHub.
3. Seleccionar el preset **FastAPI** y conservar la raíz del repositorio. Usar `main` como rama de producción y conservar los comandos detectados por el preset.
4. Pulsar **Deploy**. El simulador no requiere variables de entorno, base de datos ni dominio de pago.
5. Abrir la URL asignada. Verificar `/`, `/static/app.js`, `/static/styles.css`, `/health` y `/docs`. Calcular el ejemplo inicial y comprobar 3.4 APROBADO. Cambiar un peso para que la suma sea 110 y comprobar el mensaje.

Con la integración Git activa, verificar en el panel que los cambios de `main` generan el despliegue de producción y que una rama de trabajo genera una vista previa. Documentar el enlace y el commit de la primera versión estable. El rollback puede comprobarse cuando haya una versión anterior disponible.

- [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi)
- [Versiones de Python](https://vercel.com/docs/functions/runtimes/python/python-version)
- [Plan Hobby](https://vercel.com/docs/plans/hobby)
