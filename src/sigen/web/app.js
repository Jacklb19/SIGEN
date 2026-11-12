/* SIGEN Lite — lógica de la interfaz.
   Consume POST /api/v1/calcular del mismo origen. El servidor es la
   autoridad del cálculo: aquí solo se validan entradas, se representan
   respuestas y se presentan errores según docs/contrato_api.md. */
"use strict";

/* Configuración central del frente: rutas, valores iniciales, límites
   del contrato y textos de presentación. */
const CONFIG = {
  rutaApi: "/api/v1/calcular",
  rutaFlexible: "/api/v2/calcular",
  maxActividades: 5,
  escalaInicial: 5,
  valoresIniciales: [
    { nombre: "Parcial 1", nota: "3.5", peso: "30" },
    { nombre: "Parcial 2", nota: "2.5", peso: "30" },
    { nombre: "Proyecto", nota: "4.0", peso: "40" },
  ],
  limites: {
    nombreMin: 1,
    nombreMax: 80,
    notaMin: 0,
    decimalesNota: 1,
    pesoMin: 0,
    pesoMax: 100,
    totalPesos: 100,
  },
  textos: {
    calculando: "Calculando…",
    calcular: "Calcular definitiva",
    resumenValidacion: "Revisa los datos marcados antes de calcular.",
    errorServidor: "Ocurrió un error interno. Intenta de nuevo más tarde.",
    errorConexion:
      "No fue posible comunicarse con el servidor. Revisa tu conexión e intenta de nuevo.",
    errorRespuesta: "El servidor respondió algo inesperado. Intenta de nuevo.",
    nombreRequerido: "El nombre es obligatorio.",
    nombreLongitud: "El nombre debe tener entre 1 y 80 caracteres.",
    notaRequerida: "La nota es obligatoria, incluso si el peso es 0.",
    notaNumero: "La nota debe ser un número, por ejemplo 3.5.",
    notaPaso: "La nota debe avanzar en incrementos de 0.1.",
    pesoRequerido: "El peso es obligatorio.",
    pesoEntero: "El peso debe ser un número entero, por ejemplo 30.",
    pesoRango: "El peso debe estar entre 0 y 100.",
    aprobado: "APROBADO",
    reprobado: "REPROBADO",
  },
};

const CAMPOS = ["nombre", "nota", "peso"];

const formulario = document.getElementById("formulario");
const resumenErrores = document.getElementById("resumen-errores");
const resumenTexto = document.getElementById("resumen-errores-texto");
const resumenLista = document.getElementById("resumen-errores-lista");
const totalPesos = document.getElementById("total-pesos");
const ponderacion = document.getElementById("ponderacion");
const progresoPesos = document.getElementById("progreso-pesos");
const mensajePonderacion = document.getElementById("mensaje-ponderacion");
const materia = document.getElementById("materia");
const resultadoMateria = document.getElementById("resultado-materia");
const errorPesos = document.getElementById("error-pesos");
const botonCalcular = document.getElementById("boton-calcular");
const botonRestablecer = document.getElementById("boton-restablecer");
const seccionResultado = document.getElementById("resultado");
const avisoDesactualizado = document.getElementById("aviso-desactualizado");
const resultadoPromedio = document.getElementById("resultado-promedio");
const resultadoDefinitiva = document.getElementById("resultado-definitiva");
const resultadoEstado = document.getElementById("resultado-estado");
const semestre = document.getElementById("semestre");
const escala = document.getElementById("escala");
const agregarActividad = document.getElementById("agregar-actividad");
const quitarActividad = document.getElementById("quitar-actividad");
const contadorActividades = document.getElementById("cantidad-actividades");
const resultadoContexto = document.getElementById("resultado-contexto");

let calculoEnCurso = false;
let semestreActual = "1";
let cantidadActividades = CONFIG.valoresIniciales.length;
const borradores = new Map();

/* ---------- Utilidades de presentación ---------- */

function entrada(indice, campo) {
  return document.getElementById(`${campo}-${indice}`);
}

function elementoError(indice, campo) {
  return document.getElementById(`error-${campo}-${indice}`);
}

function mostrarErrorCampo(indice, campo, mensaje) {
  const input = entrada(indice, campo);
  const aviso = elementoError(indice, campo);
  aviso.textContent = mensaje;
  aviso.hidden = false;
  input.setAttribute("aria-invalid", "true");
  input.setAttribute("aria-describedby", aviso.id);
}

function limpiarErrorCampo(indice, campo) {
  const input = entrada(indice, campo);
  const aviso = elementoError(indice, campo);
  aviso.textContent = "";
  aviso.hidden = true;
  input.removeAttribute("aria-invalid");
  input.removeAttribute("aria-describedby");
}

function limpiarErrores() {
  for (let indice = 0; indice < cantidadActividades; indice += 1) {
    for (const campo of CAMPOS) {
      limpiarErrorCampo(indice, campo);
    }
  }
  errorPesos.textContent = "";
  errorPesos.hidden = true;
  resumenTexto.textContent = "";
  resumenLista.replaceChildren();
  resumenErrores.hidden = true;
}

function mostrarResumen(mensaje, detalles) {
  resumenTexto.textContent = mensaje;
  resumenLista.replaceChildren();
  for (const detalle of detalles || []) {
    const item = document.createElement("li");
    item.textContent = detalle;
    resumenLista.appendChild(item);
  }
  resumenErrores.hidden = false;
}

function ocultarResultado() {
  seccionResultado.hidden = true;
  seccionResultado.classList.remove("desactualizado");
  avisoDesactualizado.hidden = true;
}

function marcarResultadoDesactualizado() {
  if (!seccionResultado.hidden) {
    seccionResultado.classList.add("desactualizado");
    avisoDesactualizado.hidden = false;
  }
}

function actualizarTotalPesos() {
  const objetivo = CONFIG.limites.totalPesos;
  let suma = 0;
  for (let indice = 0; indice < cantidadActividades; indice += 1) {
    const peso = validarPeso(entrada(indice, "peso").value);
    if (peso.error) {
      totalPesos.textContent = `— / ${objetivo}`;
      progresoPesos.value = 0;
      ponderacion.classList.remove("completa", "excedida");
      mensajePonderacion.textContent = "Completa todos los pesos con valores válidos.";
      return;
    }
    suma += peso.valor;
  }
  const diferencia = objetivo - suma;
  totalPesos.textContent = `${suma} / ${objetivo}`;
  progresoPesos.value = Math.min(suma, objetivo);
  ponderacion.classList.toggle("completa", diferencia === 0);
  ponderacion.classList.toggle("excedida", diferencia < 0);

  if (diferencia === 0) {
    mensajePonderacion.textContent = "Pesos completos.";
    return;
  }
  const cantidad = Math.abs(diferencia);
  const verbo = diferencia > 0
    ? (cantidad === 1 ? "Falta" : "Faltan")
    : (cantidad === 1 ? "Sobra" : "Sobran");
  mensajePonderacion.textContent = `${verbo} ${cantidad} ${cantidad === 1 ? "punto" : "puntos"} de peso.`;
}

/* ---------- Validación de entradas (el servidor sigue siendo la autoridad) ---------- */

function validarNombre(valorCrudo) {
  const valor = valorCrudo.trim();
  if (valor.length === 0) {
    return { error: CONFIG.textos.nombreRequerido };
  }
  if (valor.length < CONFIG.limites.nombreMin || valor.length > CONFIG.limites.nombreMax) {
    return { error: CONFIG.textos.nombreLongitud };
  }
  return { valor };
}

function validarNota(valorCrudo) {
  const valor = valorCrudo.trim();
  if (valor.length === 0) {
    return { error: CONFIG.textos.notaRequerida };
  }
  if (!/^\d+(\.\d+)?$/.test(valor)) {
    return { error: CONFIG.textos.notaNumero };
  }
  const fraccion = (valor.split(".")[1] ?? "").replace(/0+$/, "");
  if (fraccion.length > CONFIG.limites.decimalesNota) {
    return { error: CONFIG.textos.notaPaso };
  }
  const numero = Number(valor);
  const maximo = Number(escala.value);
  if (!Number.isFinite(numero) || numero < CONFIG.limites.notaMin || numero > maximo) {
    return { error: `La nota debe estar entre 0 y ${maximo}.` };
  }
  return { valor: numero };
}

function validarPeso(valorCrudo) {
  const valor = valorCrudo.trim();
  if (valor.length === 0) {
    return { error: CONFIG.textos.pesoRequerido };
  }
  if (!/^\d+$/.test(valor)) {
    return { error: CONFIG.textos.pesoEntero };
  }
  const numero = Number.parseInt(valor, 10);
  if (numero < CONFIG.limites.pesoMin || numero > CONFIG.limites.pesoMax) {
    return { error: CONFIG.textos.pesoRango };
  }
  return { valor: numero };
}

/* Convierte el formulario en el objeto JSON del contrato, sin claves
   adicionales y sin convertir campos vacíos en cero. Devuelve null si
   hay errores de entrada, ya marcados en pantalla. */
function construirCarga() {
  limpiarErrores();
  const actividades = [];
  const validadores = { nombre: validarNombre, nota: validarNota, peso: validarPeso };
  let primerCampoConError = null;
  let hayErrores = false;

  for (let indice = 0; indice < cantidadActividades; indice += 1) {
    const actividad = {};
    for (const campo of CAMPOS) {
      const resultado = validadores[campo](entrada(indice, campo).value);
      if (resultado.error) {
        mostrarErrorCampo(indice, campo, resultado.error);
        hayErrores = true;
        if (primerCampoConError === null) {
          primerCampoConError = entrada(indice, campo);
        }
      } else {
        actividad[campo] = resultado.valor;
      }
    }
    actividades.push(actividad);
  }

  if (hayErrores) {
    mostrarResumen(CONFIG.textos.resumenValidacion, []);
    primerCampoConError.focus();
    return null;
  }
  const maximo = Number(escala.value);
  const flexible = cantidadActividades !== CONFIG.valoresIniciales.length ||
    maximo !== CONFIG.escalaInicial;
  return flexible ? { actividades, escala: maximo } : { actividades };
}

/* ---------- Representación del resultado ---------- */

function actualizarMateria() {
  const nombre = materia.value.trim();
  resultadoMateria.textContent = nombre;
  resultadoMateria.hidden = nombre === "";
}

function mostrarResultado(datos) {
  actualizarMateria();
  resultadoContexto.textContent = `Semestre ${semestreActual} · Escala de 0 a ${escala.value}`;
  resultadoPromedio.textContent = String(datos.promedio_ponderado);
  resultadoDefinitiva.textContent = Number(datos.nota_definitiva).toFixed(1);
  const aprobado = datos.estado === "APROBADO";
  resultadoEstado.textContent = aprobado ? CONFIG.textos.aprobado : CONFIG.textos.reprobado;
  resultadoEstado.classList.toggle("aprobado", aprobado);
  resultadoEstado.classList.toggle("reprobado", !aprobado);
  seccionResultado.classList.remove("desactualizado");
  avisoDesactualizado.hidden = true;
  seccionResultado.hidden = false;
}

function esResultadoValido(datos) {
  return (
    datos !== null &&
    typeof datos === "object" &&
    typeof datos.promedio_ponderado === "number" &&
    typeof datos.nota_definitiva === "number" &&
    (datos.estado === "APROBADO" || datos.estado === "REPROBADO") &&
    Number.isInteger(datos.ponderacion_total)
  );
}

/* ---------- Manejo de errores del contrato ---------- */

/* Ubica cada error de campo según su ruta (índices desde cero). No
   depende del orden de la lista ni del texto literal de los mensajes. */
function atenderErrorValidacion(cuerpo) {
  const campos = cuerpo && cuerpo.error && Array.isArray(cuerpo.error.campos)
    ? cuerpo.error.campos
    : [];
  const sinUbicar = [];
  let primerCampoConError = null;

  for (const fallo of campos) {
    const ruta = typeof fallo.ruta === "string" ? fallo.ruta : "";
    const mensaje = typeof fallo.mensaje === "string" && fallo.mensaje.length > 0
      ? fallo.mensaje
      : CONFIG.textos.resumenValidacion;
    const coincidencia = /^actividades\.(\d+)\.(nombre|nota|peso)$/.exec(ruta);

    if (coincidencia) {
      const indice = Number.parseInt(coincidencia[1], 10);
      const campo = coincidencia[2];
      if (indice >= 0 && indice < cantidadActividades) {
        mostrarErrorCampo(indice, campo, mensaje);
        if (primerCampoConError === null) {
          primerCampoConError = entrada(indice, campo);
        }
        continue;
      }
    }
    if (ruta === "actividades.pesos") {
      errorPesos.textContent = mensaje;
      errorPesos.hidden = false;
      continue;
    }
    sinUbicar.push(mensaje);
  }

  mostrarResumen(CONFIG.textos.resumenValidacion, sinUbicar);
  return primerCampoConError ?? resumenErrores;
}

function atenderPonderacionInvalida(cuerpo) {
  const campos = cuerpo && cuerpo.error && Array.isArray(cuerpo.error.campos)
    ? cuerpo.error.campos
    : [];
  const mensajeServidor = campos.length > 0 && typeof campos[0].mensaje === "string"
    ? campos[0].mensaje
    : null;
  errorPesos.textContent = mensajeServidor || CONFIG.textos.resumenValidacion;
  errorPesos.hidden = false;
  mostrarResumen(CONFIG.textos.resumenValidacion, []);
}

/* ---------- Comunicación con la API ---------- */

function establecerCargando(enCurso) {
  calculoEnCurso = enCurso;
  semestre.disabled = enCurso;
  escala.disabled = enCurso;
  actualizarControlesActividades();
  botonCalcular.disabled = enCurso;
  botonRestablecer.disabled = enCurso;
  botonCalcular.textContent = enCurso ? CONFIG.textos.calculando : CONFIG.textos.calcular;
  botonCalcular.setAttribute("aria-busy", enCurso ? "true" : "false");
  for (let indice = 0; indice < cantidadActividades; indice += 1) {
    for (const campo of CAMPOS) {
      entrada(indice, campo).disabled = enCurso;
    }
  }
}

async function calcular(evento) {
  evento.preventDefault();
  if (calculoEnCurso) {
    return;
  }
  const carga = construirCarga();
  if (carga === null) {
    return;
  }

  establecerCargando(true);
  let destinoFoco;
  try {
    const ruta = "escala" in carga ? CONFIG.rutaFlexible : CONFIG.rutaApi;
    const respuesta = await fetch(ruta, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(carga),
    });

    let cuerpo = null;
    try {
      cuerpo = await respuesta.json();
    } catch {
      cuerpo = null;
    }

    if (respuesta.ok && esResultadoValido(cuerpo)) {
      limpiarErrores();
      mostrarResultado(cuerpo);
    } else if (respuesta.ok) {
      mostrarResumen(CONFIG.textos.errorRespuesta, []);
    } else if (respuesta.status === 422) {
      ocultarResultado();
      destinoFoco = atenderErrorValidacion(cuerpo);
    } else if (respuesta.status === 400) {
      ocultarResultado();
      atenderPonderacionInvalida(cuerpo);
    } else if (respuesta.status >= 500) {
      ocultarResultado();
      mostrarResumen(CONFIG.textos.errorServidor, []);
    } else {
      ocultarResultado();
      mostrarResumen(CONFIG.textos.errorRespuesta, []);
    }
  } catch {
    ocultarResultado();
    mostrarResumen(CONFIG.textos.errorConexion, []);
  } finally {
    establecerCargando(false);
    destinoFoco?.focus();
  }
}

/* ---------- Restablecer y cambios ---------- */

function actualizarControlesActividades() {
  const minimo = CONFIG.valoresIniciales.length;
  agregarActividad.disabled = calculoEnCurso || cantidadActividades >= CONFIG.maxActividades;
  quitarActividad.disabled = calculoEnCurso || cantidadActividades <= minimo;
  contadorActividades.textContent = `${cantidadActividades} de ${CONFIG.maxActividades} actividades`;
}

function actualizarFilas() {
  for (let indice = CONFIG.valoresIniciales.length; indice < CONFIG.maxActividades; indice += 1) {
    const fila = document.getElementById(`actividad-extra-${indice}`);
    fila.hidden = indice >= cantidadActividades;
    fila.disabled = fila.hidden;
  }
  actualizarControlesActividades();
}

function actualizarEscala() {
  const etiqueta = `Nota (0–${escala.value})`;
  document.getElementById("encabezado-nota").textContent = etiqueta;
  for (let indice = 0; indice < CONFIG.maxActividades; indice += 1) {
    document.getElementById(`etiqueta-nota-${indice}`).textContent = etiqueta;
  }
}

function actividadVacia(indice) {
  return { nombre: `Actividad ${indice + 1}`, nota: "", peso: "" };
}

function guardarBorrador() {
  const actividades = Array.from({ length: cantidadActividades }, (_, indice) =>
    Object.fromEntries(CAMPOS.map((campo) => [campo, entrada(indice, campo).value]))
  );
  borradores.set(semestreActual, { materia: materia.value, escala: escala.value, actividades });
}

function valoresDelSemestre() {
  const actividades = semestreActual === "1"
    ? CONFIG.valoresIniciales
    : CONFIG.valoresIniciales.map((_, indice) => actividadVacia(indice));
  return { materia: "", escala: String(CONFIG.escalaInicial), actividades };
}

function cargarBorrador(borrador) {
  limpiarErrores();
  cantidadActividades = borrador.actividades.length;
  materia.value = borrador.materia;
  escala.value = borrador.escala;
  actualizarMateria();
  borrador.actividades.forEach((actividad, indice) => {
    for (const campo of CAMPOS) {
      entrada(indice, campo).value = actividad[campo];
    }
  });
  actualizarFilas();
  actualizarEscala();
  ocultarResultado();
  actualizarTotalPesos();
}

function cambiarSemestre() {
  guardarBorrador();
  semestreActual = semestre.value;
  cargarBorrador(borradores.get(semestreActual) ?? valoresDelSemestre());
}

function cambiarCantidad(delta) {
  const siguiente = cantidadActividades + delta;
  if (siguiente < CONFIG.valoresIniciales.length || siguiente > CONFIG.maxActividades) {
    return;
  }
  limpiarErrores();
  if (delta > 0) {
    const nueva = actividadVacia(cantidadActividades);
    for (const campo of CAMPOS) {
      entrada(cantidadActividades, campo).value = nueva[campo];
    }
  }
  cantidadActividades = siguiente;
  actualizarFilas();
  marcarResultadoDesactualizado();
  actualizarTotalPesos();
  entrada(cantidadActividades - 1, "nombre").focus();
}

function restablecer() {
  cargarBorrador(valoresDelSemestre());
  entrada(0, "nombre").focus();
}

function alEditarCampo(evento) {
  const input = evento.target;
  if (input === materia) {
    actualizarMateria();
    return;
  }
  if (!(input instanceof HTMLInputElement)) {
    return;
  }
  marcarResultadoDesactualizado();
  const actividad = input.closest(".actividad");
  if (actividad) {
    limpiarErrorCampo(Number(actividad.dataset.indice), input.dataset.campo);
  }
  actualizarTotalPesos();
}

/* ---------- Arranque ---------- */

semestre.value = semestreActual;
cargarBorrador(valoresDelSemestre());
semestre.addEventListener("change", cambiarSemestre);
escala.addEventListener("change", () => {
  actualizarEscala();
  limpiarErrores();
  marcarResultadoDesactualizado();
});
agregarActividad.addEventListener("click", () => cambiarCantidad(1));
quitarActividad.addEventListener("click", () => cambiarCantidad(-1));
formulario.addEventListener("submit", calcular);
formulario.addEventListener("input", alEditarCampo);
botonRestablecer.addEventListener("click", restablecer);
