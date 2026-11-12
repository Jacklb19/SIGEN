const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

function cargarInterfaz(respuesta) {
  const directorios = ["../../src/sigen/web", "../../web"];
  const archivo = directorios
    .map((directorio) => path.join(__dirname, directorio, "app.js"))
    .find((candidato) => fs.existsSync(candidato));
  const elementos = new Map();
  const peticiones = [];
  const documento = {
    activeElement: null,
    createElement: () => ({}),
    getElementById(id) {
      if (!elementos.has(id)) {
        elementos.set(id, {
          id,
          listeners: {},
          disabled: false,
          classList: { add() {}, remove() {}, toggle() {} },
          addEventListener(evento, callback) { this.listeners[evento] = callback; },
          appendChild() {},
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
    async fetch(url, opciones) {
      peticiones.push(JSON.parse(opciones.body));
      return respuesta;
    },
  });
  return {
    elemento: (id) => documento.getElementById(id),
    foco: () => documento.activeElement?.id,
    peticiones,
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
