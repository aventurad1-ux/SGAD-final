
<template>
  <div class="bitacora-page">
    <div class="bitacora-header">
      <div>
        <h1>Bitácora de actividades</h1>
        <p>
          Consulta los movimientos y actividades
          realizadas dentro del sistema SGAD.
        </p>
      </div>
      <button class="btn-refresh" @click="cargarRegistros">
        Actualizar
      </button>
    </div>

    <form class="filtros" @submit.prevent="buscar">
      <div class="campo">
        <label>Usuario</label>
        <input
          v-model="filtros.usuario"
          type="text"
          placeholder="Buscar usuario"
        />
      </div>

      <div class="campo">
        <label>Acción</label>
        <input
          v-model="filtros.accion"
          type="text"
          placeholder="Ej. CREAR"
        />
      </div>

      <div class="campo">
        <label>Módulo</label>
        <input
          v-model="filtros.modulo"
          type="text"
          placeholder="Ej. Expedientes"
        />
      </div>

      <div class="acciones-filtros">
        <button type="submit" class="btn-primary">
          Buscar
        </button>
        <button
          type="button"
          class="btn-secondary"
          @click="limpiar"
        >
          Limpiar
        </button>
      </div>
    </form>

    <div class="bitacora-tabla">
      <div class="tabla-header">
        <h2>Historial de actividades</h2>
        <span>Total: {{ total }}</span>
      </div>

      <p v-if="cargando" class="mensaje">
        Cargando actividades...
      </p>

      <p v-else-if="error" class="mensaje error">
        {{ error }}
      </p>

      <div v-else class="tabla-scroll">
        <table>
          <thead>
            <tr>
              <th>Fecha y hora</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Módulo</th>
              <th>Descripción</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="registro in registros"
              :key="registro.id_bitacora"
            >
              <td>
                {{ formatearFecha(registro.fecha_hora) }}
              </td>
              <td>
                {{ registro.usuario || "No disponible" }}
              </td>
              <td>
                <span class="etiqueta">
                  {{ registro.accion }}
                </span>
              </td>
              <td>{{ registro.modulo }}</td>
              <td>{{ registro.descripcion || "—" }}</td>
            </tr>

            <tr v-if="registros.length === 0">
              <td colspan="5" class="sin-datos">
                No se encontraron actividades.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!cargando && !error" class="paginacion">
        <button
          :disabled="pagina <= 1"
          @click="cambiarPagina(pagina - 1)"
        >
          Anterior
        </button>

        <span>Página {{ pagina }} de {{ paginas }}</span>

        <button
          :disabled="pagina >= paginas"
          @click="cambiarPagina(pagina + 1)"
        >
          Siguiente
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { obtenerBitacora } from "../../services/bitacoraService";

const registros = ref([]);
const cargando = ref(false);
const error = ref("");

const pagina = ref(1);
const paginas = ref(1);
const total = ref(0);

const filtros = ref({
  usuario: "",
  accion: "",
  modulo: "",
});

async function cargarRegistros() {
  cargando.value = true;
  error.value = "";

  try {
    const respuesta = await obtenerBitacora({
      ...filtros.value,
      pagina: pagina.value,
      limite: 20,
    });

    registros.value = respuesta.registros || [];
    total.value = respuesta.total || 0;
    paginas.value = Math.max(respuesta.paginas || 1, 1);
  } catch (err) {
    registros.value = [];
    total.value = 0;
    paginas.value = 1;

    error.value =
      "No fue posible cargar la bitácora. Verifica tu sesión y los permisos de acceso.";
    console.error("Error al consultar bitácora:", err);
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
    usuario: "",
    accion: "",
    modulo: "",
  };

  pagina.value = 1;
  cargarRegistros();
}

function cambiarPagina(nuevaPagina) {
  if (nuevaPagina < 1 || nuevaPagina > paginas.value) {
    return;
  }

  pagina.value = nuevaPagina;
  cargarRegistros();
}

function formatearFecha(fecha) {
  if (!fecha) return "—";

  const valor = new Date(fecha);

  if (Number.isNaN(valor.getTime())) {
    return fecha;
  }

  return valor.toLocaleString("es-GT");
}

onMounted(cargarRegistros);
</script>

<style scoped>
.bitacora-page {
  padding: 24px;
  color: #263449;
}

.bitacora-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.bitacora-header h1 {
  margin: 0 0 8px;
  font-size: 26px;
}

.bitacora-header p {
  margin: 0;
  color: #64748b;
}

.filtros {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 14px;
  padding: 20px;
  margin-bottom: 24px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.campo {
  flex: 1 1 170px;
}

.campo label {
  display: block;
  margin-bottom: 7px;
  font-weight: 600;
  font-size: 13px;
}

.campo input {
  box-sizing: border-box;
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
}

.acciones-filtros {
  display: flex;
  gap: 8px;
}

button {
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
  background: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-primary,
.btn-refresh {
  background: #245a85;
  border-color: #245a85;
  color: white;
}

.bitacora-tabla {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.tabla-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px;
  gap: 12px;
}

.tabla-header h2 {
  margin: 0;
  font-size: 18px;
}

.tabla-header span {
  color: #64748b;
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
  padding: 13px;
  border-top: 1px solid #e2e8f0;
  text-align: left;
  font-size: 13px;
}

th {
  background: #f8fafc;
}

.etiqueta {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 6px;
  background: #e8f1fa;
  color: #245a85;
  font-weight: 600;
}

.mensaje,
.sin-datos {
  padding: 24px;
  text-align: center;
  color: #64748b;
}

.error {
  color: #b42318;
}

.paginacion {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  padding: 18px;
  border-top: 1px solid #e2e8f0;
}

@media (max-width: 600px) {
  .bitacora-page {
    padding: 12px;
  }

  .bitacora-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
