const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

function cargarInterfaz(respuesta) {
  const archivo = path.join(__dirname, "../../src/sigen/web/app.js");
  const elementos = new Map();
  const peticiones = [];
  const documento = {
    activeElement: null,
    createElement: () => ({}),
    getElementById(id) {
      if (!elementos.has(id)) {
        elementos.set(id, {
          id,
          value: "",
          listeners: {},
          disabled: false,
          classList: { add() {}, remove() {}, toggle() {} },
          addEventListener(evento, callback) { this.listeners[evento] = callback; },
          appendChild() {},
          closest() { return null; },
          replaceChildren() {},
          setAttribute() {},
          removeAttribute() {},
          focus() {
            if (!this.disabled) documento.activeElement = this;
          },
        });
      }
      return elementos.get(id);
    },
  };
  vm.runInNewContext(fs.readFileSync(archivo, "utf8"), {
    document: documento,
    HTMLInputElement: Object,
    async fetch(url, opciones) {
      peticiones.push(JSON.parse(opciones.body));
      return respuesta;
    },
  });
  return {
    elemento: (id) => documento.getElementById(id),
    foco: () => documento.activeElement?.id,
    peticiones,
    editar(id, valor) {
      const target = documento.getElementById(id);
      target.value = valor;
      documento.getElementById("formulario").listeners.input({ target });
    },
    restablecer: () => documento.getElementById("boton-restablecer").listeners.click(),
    enviar: () => documento.getElementById("formulario").listeners.submit({
      preventDefault() {},
    }),
  };
}

test("rechaza una nota que Number redondearía a un valor válido", async () => {
  const ui = cargarInterfaz();
  ui.elemento("nota-0").value = "3.5000000000000000000000000001";
  await ui.enviar();
  assert.equal(ui.peticiones.length, 0);
  assert.equal(ui.elemento("error-nota-0").hidden, false);
});

test("admite los ceros finales sin cambiar el valor de la nota", async () => {
  const ui = cargarInterfaz({
    ok: true,
    json: async () => ({
      promedio_ponderado: 3.4,
      nota_definitiva: 3.4,
      estado: "APROBADO",
      ponderacion_total: 100,
    }),
  });
  ui.elemento("nota-0").value = "3.50";
  await ui.enviar();
  assert.equal(ui.peticiones[0].actividades[0].nota, 3.5);
  assert.equal(ui.elemento("resultado-definitiva").textContent, "3.4");
});

test("enfoca el campo señalado por el servidor tras habilitar el formulario", async () => {
  const ui = cargarInterfaz({
    ok: false,
    status: 422,
    json: async () => ({
      error: { campos: [{ ruta: "actividades.1.nota", mensaje: "Revisa la nota." }] },
    }),
  });
  await ui.enviar();
  assert.equal(ui.elemento("nota-1").disabled, false);
  assert.equal(ui.foco(), "nota-1");
});

test("informa pesos faltantes, excedentes, completos e incompletos", () => {
  const ui = cargarInterfaz();
  const mensaje = ui.elemento("mensaje-ponderacion");
  assert.equal(mensaje.textContent, "Pesos completos.");
  ui.editar("peso-2", "30");
  assert.equal(mensaje.textContent, "Faltan 10 puntos de peso.");
  assert.equal(ui.elemento("progreso-pesos").value, 90);
  ui.editar("peso-2", "50");
  assert.equal(mensaje.textContent, "Sobran 10 puntos de peso.");
  assert.equal(ui.elemento("total-pesos").textContent, "110 / 100");
  assert.equal(ui.elemento("progreso-pesos").value, 100);
  ui.editar("peso-2", "");
  assert.equal(mensaje.textContent, "Completa los tres pesos con valores válidos.");
});

test("muestra la materia solo en el resultado y la limpia al restablecer", async () => {
  const ui = cargarInterfaz({
    ok: true,
    json: async () => ({
      promedio_ponderado: 3.375,
      nota_definitiva: 3.4,
      estado: "APROBADO",
      ponderacion_total: 100,
    }),
  });
  ui.editar("materia", "  Pruebas y Mantenimiento  ");
  ui.editar("peso-0", "20");
  ui.editar("peso-1", "35");
  ui.editar("peso-2", "45");
  await ui.enviar();
  assert.deepEqual(Object.keys(ui.peticiones[0]), ["actividades"]);
  assert.deepEqual(ui.peticiones[0].actividades.map((actividad) => actividad.peso), [20, 35, 45]);
  assert.equal(ui.elemento("resultado-materia").textContent, "Pruebas y Mantenimiento");
  assert.equal(ui.elemento("resultado-materia").hidden, false);
  assert.equal(ui.elemento("resultado-definitiva").textContent, "3.4");
  ui.restablecer();
  assert.equal(ui.elemento("materia").value, "");
  assert.equal(ui.elemento("resultado-materia").hidden, true);
  assert.equal(ui.elemento("resultado").hidden, true);
  assert.equal(ui.elemento("mensaje-ponderacion").textContent, "Pesos completos.");
});
