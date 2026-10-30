<template>
  <div class="bitacora-layout">
    <DirectorSidebar />

    <main class="bitacora-main">
      <DirectorTopbar />

      <section class="bitacora-content">
        <header class="bitacora-heading">
          <span class="bitacora-eyebrow">
            SEGURIDAD
          </span>

          <h1>
            Bitácora de actividad
          </h1>

          <p>
            Consulte quién realizó cada acción importante
            dentro del sistema SGAD.
          </p>
        </header>

        <section class="filtros-card">
          <div class="busqueda-general">
            <span class="busqueda-icono">
              ⌕
            </span>

            <input
              v-model="filtros.busqueda"
              type="text"
              placeholder="Buscar acción, registro o detalles..."
              @keyup.enter="buscar"
            />
          </div>

          <div class="filtro-select">
            <select
              v-model="filtros.id_usuario"
              @change="buscar"
            >
              <option value="">
                Todos los usuarios
              </option>

              <option
                v-for="usuario in usuarios"
                :key="usuario.id_usuario"
                :value="usuario.id_usuario"
              >
                {{ usuario.nombre }}
              </option>
            </select>
          </div>

          <div class="filtro-fecha">
            <label>
              Fecha desde
            </label>

            <input
              v-model="filtros.fecha_desde"
              type="date"
              @change="buscar"
            />
          </div>

          <div class="filtro-fecha">
            <label>
              Fecha hasta
            </label>

            <input
              v-model="filtros.fecha_hasta"
              type="date"
              @change="buscar"
            />
          </div>

          <button
            type="button"
            class="btn-limpiar"
            @click="limpiar"
          >
            Limpiar
          </button>
        </section>

        <section class="bitacora-card">
          <div class="tabla-header">
            <div>
              <span class="tabla-eyebrow">
                HISTORIAL
              </span>

              <h2>
                Actividades registradas
              </h2>
            </div>

            <span class="total-registros">
              Total: {{ total }}
            </span>
          </div>

          <div
            v-if="cargando"
            class="mensaje"
          >
            Cargando actividades...
          </div>

          <div
            v-else-if="error"
            class="mensaje error"
          >
            {{ error }}
          </div>

          <div
            v-else
            class="tabla-scroll"
          >
            <table>
              <thead>
                <tr>
                  <th>Fecha y hora</th>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Módulo</th>
                  <th>Registro</th>
                  <th>Detalles</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="registro in registros"
                  :key="registro.id_bitacora"
                >
                  <td class="fecha">
                    {{
                      formatearFecha(
                        registro.fecha_hora
                      )
                    }}
                  </td>

                  <td>
                    <strong>
                      {{
                        registro.usuario ||
                        "Usuario no disponible"
                      }}
                    </strong>
                  </td>

                  <td>
                    <span class="accion-badge">
                      {{
                        formatearAccion(
                          registro.accion
                        )
                      }}
                    </span>
                  </td>

                  <td>
                    {{
                      formatearModulo(
                        registro.modulo
                      )
                    }}
                  </td>

                  <td class="registro-col">
                    {{
                      registro.registro ||
                      "—"
                    }}
                  </td>

                  <td class="detalle-col">
                    {{
                      registro.descripcion ||
                      "—"
                    }}
                  </td>
                </tr>

                <tr
                  v-if="registros.length === 0"
                >
                  <td
                    colspan="6"
                    class="sin-datos"
                  >
                    No se encontraron actividades.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div
            v-if="!cargando && !error"
            class="paginacion"
          >
            <button
              type="button"
              :disabled="pagina <= 1"
              @click="cambiarPagina(pagina - 1)"
            >
              Anterior
            </button>

            <span>
              Página {{ pagina }} de {{ paginas }}
            </span>

            <button
              type="button"
              :disabled="pagina >= paginas"
              @click="cambiarPagina(pagina + 1)"
            >
              Siguiente
            </button>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import {
  ref,
  onMounted
} from "vue";

import DirectorSidebar
  from "../../components/layout/DirectorSidebar.vue";

import DirectorTopbar
  from "../../components/layout/DirectorTopbar.vue";

import {
  obtenerBitacora,
  obtenerUsuariosBitacora
} from "../../services/bitacoraService";


const registros = ref([]);
const usuarios = ref([]);

const cargando = ref(false);
const error = ref("");

const pagina = ref(1);
const paginas = ref(1);
const total = ref(0);

const filtros = ref({
  busqueda: "",
  id_usuario: "",
  fecha_desde: "",
  fecha_hasta: ""
});


async function cargarUsuarios() {
  try {
    const respuesta =
      await obtenerUsuariosBitacora();

    usuarios.value =
      respuesta.usuarios || [];

  } catch (err) {
    console.error(
      "Error al cargar usuarios de bitácora:",
      err
    );

    usuarios.value = [];
  }
}


async function cargarRegistros() {
  cargando.value = true;
  error.value = "";

  try {
    const parametros = {
      pagina: pagina.value,
      limite: 20
    };

    if (filtros.value.busqueda) {
      parametros.busqueda =
        filtros.value.busqueda;
    }

    if (filtros.value.id_usuario) {
      parametros.id_usuario =
        filtros.value.id_usuario;
    }

    if (filtros.value.fecha_desde) {
      parametros.fecha_desde =
        filtros.value.fecha_desde;
    }

    if (filtros.value.fecha_hasta) {
      parametros.fecha_hasta =
        filtros.value.fecha_hasta;
    }

    const respuesta =
      await obtenerBitacora(
        parametros
      );

    registros.value =
      respuesta.registros || [];

    total.value =
      respuesta.total || 0;

    paginas.value =
      Math.max(
        respuesta.paginas || 1,
        1
      );

  } catch (err) {
    registros.value = [];
    total.value = 0;
    paginas.value = 1;

    error.value =
      err.response?.data?.mensaje ||
      "No fue posible cargar la bitácora.";

    console.error(
      "Error al consultar bitácora:",
      err
    );

  } finally {
    cargando.value = false;
  }
}


function buscar() {
  pagina.value = 1;
  cargarRegistros();
}


function limpiar() {
  filtros.value = {
    busqueda: "",
    id_usuario: "",
    fecha_desde: "",
    fecha_hasta: ""
  };

  pagina.value = 1;

  cargarRegistros();
}


function cambiarPagina(
  nuevaPagina
) {
  if (
    nuevaPagina < 1 ||
    nuevaPagina > paginas.value
  ) {
    return;
  }

  pagina.value =
    nuevaPagina;

  cargarRegistros();
}


function formatearFecha(
  fecha
) {
  if (!fecha) {
    return "—";
  }

  const valor =
    new Date(fecha);

  if (
    Number.isNaN(
      valor.getTime()
    )
  ) {
    return fecha;
  }

  return valor.toLocaleString(
    "es-GT",
    {
      dateStyle: "short",
      timeStyle: "short"
    }
  );
}


function formatearAccion(
  accion
) {
  if (!accion) {
    return "—";
  }

  return accion
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /^\w/,
      letra =>
        letra.toUpperCase()
    );
}


function formatearModulo(
  modulo
) {
  if (!modulo) {
    return "—";
  }

  return modulo
    .replaceAll("_", " ")
    .replace(
      /^\w/,
      letra =>
        letra.toUpperCase()
    );
}


onMounted(
  async () => {
    await cargarUsuarios();
    await cargarRegistros();
  }
);
</script>

<style scoped>
.bitacora-layout {
  min-height: 100vh;
  background: #f3f8fc;
}

.bitacora-main {
  min-height: 100vh;
  margin-left: 286px;
}

.bitacora-content {
  padding: 36px 40px 60px;
}

.bitacora-heading {
  margin-bottom: 24px;
}

.bitacora-eyebrow,
.tabla-eyebrow {
  display: block;
  margin-bottom: 7px;
  color: #1e84b8;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 2px;
}

.bitacora-heading h1 {
  margin: 0;
  color: #07507d;
  font-size: 38px;
  line-height: 1.1;
}

.bitacora-heading p {
  margin: 8px 0 0;
  color: #688091;
  font-size: 15px;
}

.filtros-card {
  display: grid;
  grid-template-columns:
    minmax(280px, 1.6fr)
    minmax(200px, 1fr)
    minmax(160px, 0.8fr)
    minmax(160px, 0.8fr)
    auto;

  gap: 12px;
  align-items: end;

  margin-bottom: 18px;
  padding: 16px;

  border: 1px solid #d3e3ed;
  border-radius: 16px;

  background: #ffffff;
}

.busqueda-general {
  position: relative;
}

.busqueda-icono {
  position: absolute;
  top: 50%;
  left: 14px;

  transform: translateY(-50%);

  color: #6f8898;
  font-size: 20px;
}

.busqueda-general input,
.filtro-select select,
.filtro-fecha input {
  box-sizing: border-box;
  width: 100%;
  height: 48px;

  border: 1px solid #c9dce8;
  border-radius: 10px;

  background: #ffffff;

  color: #294f67;
  font-size: 14px;

  outline: none;
}

.busqueda-general input {
  padding: 0 14px 0 42px;
}

.filtro-select select,
.filtro-fecha input {
  padding: 0 12px;
}

.filtro-fecha label {
  display: block;
  margin-bottom: 6px;

  color: #4d6879;
  font-size: 11px;
  font-weight: 700;
}

.btn-limpiar {
  height: 48px;
  padding: 0 18px;

  border: 1px solid #c6d9e5;
  border-radius: 10px;

  background: #ffffff;
  color: #315d75;

  font-weight: 700;
  cursor: pointer;
}

.btn-limpiar:hover {
  background: #f4fafc;
}

.bitacora-card {
  overflow: hidden;

  border: 1px solid #d3e3ed;
  border-radius: 18px;

  background: #ffffff;
}

.tabla-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  gap: 16px;
  padding: 20px 24px;
}

.tabla-header h2 {
  margin: 0;
  color: #07507d;
  font-size: 21px;
}

.total-registros {
  color: #728796;
  font-size: 13px;
}

.tabla-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 16px;
  border-top: 1px solid #e2edf3;
  text-align: left;
  vertical-align: middle;
}

th {
  background: #f8fbfd;

  color: #6c8190;
  font-size: 10px;
  font-weight: 800;

  letter-spacing: 0.7px;
  text-transform: uppercase;
}

td {
  color: #315469;
  font-size: 13px;
}

tbody tr:hover {
  background: #f8fcfe;
}

.fecha {
  min-width: 145px;
}

.accion-badge {
  display: inline-flex;

  padding: 5px 8px;

  border-radius: 7px;

  background: #e9f2fa;
  color: #245c86;

  font-size: 11px;
  font-weight: 700;
}

.registro-col {
  min-width: 160px;
  color: #144b6a;
  font-weight: 600;
}

.detalle-col {
  min-width: 220px;
}

.mensaje,
.sin-datos {
  padding: 36px;
  text-align: center;
  color: #708696;
}

.error {
  color: #b42318;
}

.paginacion {
  display: flex;
  justify-content: center;
  align-items: center;

  gap: 14px;

  padding: 16px;

  border-top: 1px solid #e2edf3;
}

.paginacion button {
  padding: 8px 14px;

  border: 1px solid #c8dce8;
  border-radius: 8px;

  background: #ffffff;
  color: #07507d;

  font-weight: 700;
  cursor: pointer;
}

.paginacion button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.paginacion span {
  color: #587383;
  font-size: 13px;
}

@media (max-width: 1200px) {
  .filtros-card {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .btn-limpiar {
    width: 100%;
  }
}

@media (max-width: 1000px) {
  .bitacora-main {
    margin-left: 0;
  }
}

@media (max-width: 720px) {
  .bitacora-content {
    padding: 24px 16px 40px;
  }

  .bitacora-heading h1 {
    font-size: 31px;
  }

  .filtros-card {
    grid-template-columns: 1fr;
  }

  .tabla-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>